from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from order.models import Order
from order.serializers import OrderSerializer

from accounts.models import User
from accounts.sms import send_sms

from .models import Payment, PaymentStatus
from .serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
)
from .services import PaymentService

import jdatetime


# =========================================================
# CREATE PAYMENT
# =========================================================

class PaymentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Payment"],
        summary="ایجاد درخواست پرداخت",
        description=(
            "برای سفارش یک درخواست پرداخت ایجاد می‌کند "
            "و به درگاه ZarinPal متصل می‌شود."
        ),
        request=PaymentCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="درخواست پرداخت با موفقیت ایجاد شد."
            ),
            400: OpenApiResponse(
                description="اطلاعات پرداخت نامعتبر است."
            ),
            404: OpenApiResponse(
                description="سفارش پیدا نشد."
            ),
        },
    )
    def post(self, request):

        serializer = PaymentCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]

        # -------------------------------------------------
        # پیدا کردن سفارش متعلق به کاربر
        # -------------------------------------------------

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user,
            )

        except Order.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "سفارش مورد نظر پیدا نشد.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -------------------------------------------------
        # Callback URL
        # -------------------------------------------------

        callback_url = request.build_absolute_uri(
            reverse("payment:payment-callback")
        )

        # -------------------------------------------------
        # Create Payment
        # -------------------------------------------------

        try:
            result = PaymentService.create_payment(
                user=request.user,
                order=order,
                callback_url=callback_url,
            )

        except DjangoValidationError as exc:

            if hasattr(exc, "message_dict"):
                detail = exc.message_dict
            else:
                detail = exc.messages

            return Response(
                {
                    "success": False,
                    "message": "ایجاد درخواست پرداخت ناموفق بود.",
                    "detail": detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = result["payment"]

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return Response(
            {
                "success": True,
                "message": "درخواست پرداخت با موفقیت ایجاد شد.",

                "payment": PaymentSerializer(
                    payment
                ).data,

                "payment_url": result["payment_url"],

                "is_new": result["is_new"],
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# PAYMENT CALLBACK
# =========================================================

class PaymentCallbackAPIView(APIView):

    # =========================================================
    # FRONTEND URLS
    # =========================================================

    FRONTEND_SUCCESS_URL = (
        "http://localhost:3000/checkout/success"
    )

    FRONTEND_FAILED_URL = (
        "http://localhost:3000/checkout/failed"
    )

    @extend_schema(
        tags=["Payment"],
        summary="Callback درگاه پرداخت",
        description=(
            "Callback ارسال‌شده توسط ZarinPal را دریافت می‌کند. "
            "در صورت موفق بودن پرداخت، تراکنش Verify شده و "
            "سفارش نهایی می‌شود."
        ),
        responses={
            200: OpenApiResponse(
                description="پرداخت با موفقیت تأیید شد."
            ),
            400: OpenApiResponse(
                description="پرداخت ناموفق یا لغو شده است."
            ),
            404: OpenApiResponse(
                description="پرداخت پیدا نشد."
            ),
        },
    )
    def get(self, request):

        authority = request.query_params.get("Authority")
        gateway_status = request.query_params.get("Status")

        # =================================================
        # CHECK AUTHORITY
        # =================================================

        if not authority:

            return redirect(
                f"{self.FRONTEND_FAILED_URL}"
                f"?reason=missing_authority"
            )

        # =================================================
        # FIND PAYMENT
        # =================================================

        try:
            payment = (
                Payment.objects
                .select_related(
                    "order",
                    "user",
                )
                .get(
                    authority=authority
                )
            )

        except Payment.DoesNotExist:

            return redirect(
                f"{self.FRONTEND_FAILED_URL}"
                f"?reason=payment_not_found"
            )

        # =================================================
        # ALREADY VERIFIED
        # =================================================

        if payment.status == PaymentStatus.SUCCESS:

            order = payment.order

            return redirect(
                f"{self.FRONTEND_SUCCESS_URL}"
                f"?tracking_code={order.tracking_code}"
                f"&order_id={order.id}"
                f"&payment_id={payment.id}"
            )

        # =================================================
        # PAYMENT CANCELED BY USER
        # =================================================

        if gateway_status != "OK":

            payment.status = PaymentStatus.CANCELED

            existing_gateway_data = (
                payment.gateway_data
                if isinstance(
                    payment.gateway_data,
                    dict
                )
                else {}
            )

            payment.gateway_data = {
                **existing_gateway_data,

                "callback": {
                    "Authority": authority,
                    "Status": gateway_status,
                },
            }

            payment.error_code = "PAYMENT_CANCELED"

            payment.error_message = (
                "کاربر پرداخت را لغو کرد."
            )

            payment.save(
                update_fields=[
                    "status",
                    "gateway_data",
                    "error_code",
                    "error_message",
                    "updated_date",
                ]
            )

            # -------------------------------------------------
            # SMS ناموفق فقط برای مشتری
            # -------------------------------------------------

            profile = getattr(payment.user, "profile", None)

            if profile:
                customer_name = profile.get_fullname()
            else:
                customer_name = "کاربر"

            if customer_name == "کاربر جدید":
                customer_name = "کاربر"

            failed_sms = (
                f"{customer_name} عزیز، پرداخت سفارش شما ناموفق بود.\n\n"
                "لطفاً مجدداً برای پرداخت اقدام کنید.\n"
                "در صورت کسر وجه، مبلغ طبق روال بانکی "
                "به حساب شما بازگردانده خواهد شد.\n\n"
                "فروشگاه لوما"
            )

            send_sms(
                to=payment.user.phone_number,
                text=failed_sms,
            )

            # -------------------------------------------------
            # Cart دست نمی‌خورد
            # Stock دست نمی‌خورد
            # Coupon مصرف نمی‌شود
            # -------------------------------------------------

            return redirect(
                f"{self.FRONTEND_FAILED_URL}"
                f"?payment_id={payment.id}"
                f"&reason=canceled"
            )

        # =================================================
        # VERIFY PAYMENT
        # =================================================

        try:

            result = PaymentService.verify_payment(
                payment=payment
            )

        except DjangoValidationError:

            return redirect(
                f"{self.FRONTEND_FAILED_URL}"
                f"?payment_id={payment.id}"
                f"&reason=verify_error"
            )

        # =================================================
        # VERIFY FAILED
        # =================================================

        if not result["success"]:

            payment = result["payment"]

            failed_sms = (
                "پرداخت سفارش شما ناموفق بود.\n\n"
                "لطفاً مجدداً برای پرداخت اقدام کنید.\n"
                "در صورت کسر وجه، مبلغ طبق روال بانکی "
                "به حساب شما بازگردانده خواهد شد.\n\n"
                "فروشگاه لوما"
            )

            send_sms(
                to=payment.user.phone_number,
                text=failed_sms,
            )

            return redirect(
                f"{self.FRONTEND_FAILED_URL}"
                f"?payment_id={payment.id}"
                f"&reason=payment_failed"
            )

        # =================================================
        # VERIFY SUCCESS
        # =================================================

        payment = result["payment"]
        order = result["order"]

        # =================================================
        # PAYMENT DATE & TIME - SHAMSI
        # =================================================

        payment_datetime = timezone.localtime(
            payment.updated_date
        )

        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=payment_datetime
        )

        payment_date = jalali_datetime.strftime(
            "%Y/%m/%d"
        )

        payment_time = jalali_datetime.strftime(
            "%H:%M"
        )

        # =================================================
        # SMS SUCCESS - USER
        # =================================================

        profile = getattr(payment.user, "profile", None)

        if profile:
            customer_name = profile.get_fullname()
        else:
            customer_name = "کاربر"

        if customer_name == "کاربر جدید":
            customer_name = "کاربر"

        user_sms = (
            f"{customer_name} عزیز، پرداخت سفارش شما با موفقیت انجام شد.\n\n"
            f"کد پیگیری سفارش: {order.tracking_code}\n"
            f"مبلغ پرداختی: {payment.amount:,} ریال\n\n"
            "از خرید شما سپاسگزاریم ❤️\n\n"
            "فروشگاه لوما"
        )

        send_sms(
            to=payment.user.phone_number,
            text=user_sms,
        )

        # =================================================
        # FIND ADMINS
        # =================================================

        admins = (
            User.objects
            .filter(
                role=User.Roles.ADMIN
            )
            .values_list(
                "phone_number",
                flat=True
            )
        )

        # =================================================
        # SMS SUCCESS - ADMINS
        # =================================================

        admin_sms = (
            "یک پرداخت موفق ثبت شد.\n\n"
            f"کد سفارش: {order.tracking_code}\n"
            f"شماره مشتری: {payment.user.phone_number}\n"
            f"مبلغ پرداختی: {payment.amount:,} ریال\n"
            f"تاریخ پرداخت: {payment_date}\n"
            f"ساعت پرداخت: {payment_time}\n\n"
            "سفارش آماده بررسی است.\n\n"
            "فروشگاه لوما"
        )

        for admin_phone in admins:

            send_sms(
                to=admin_phone,
                text=admin_sms,
            )

        # =================================================
        # REDIRECT TO FRONTEND
        # =================================================

        return redirect(
            f"{self.FRONTEND_SUCCESS_URL}"
            f"?tracking_code={order.tracking_code}"
            f"&order_id={order.id}"
            f"&payment_id={payment.id}"
        )