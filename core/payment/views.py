from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse

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

from .models import Payment, PaymentStatus
from .serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
)
from .services import PaymentService
from django.shortcuts import redirect


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

        except DjangoValidationError as exc:

            if hasattr(exc, "message_dict"):
                detail = exc.message_dict
            else:
                detail = exc.messages

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
        # SMS
        # =================================================

        user_sms = (
            f"پرداخت سفارش شما با موفقیت انجام شد. "
            f"شماره پیگیری: {order.tracking_code} "
            f"- مبلغ: {payment.amount}"
        )

        admin_sms = (
            f"سفارش جدید با موفقیت پرداخت شد. "
            f"شماره پیگیری: {order.tracking_code} "
            f"- کاربر: {payment.user.phone_number} "
            f"- مبلغ: {payment.amount}"
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

