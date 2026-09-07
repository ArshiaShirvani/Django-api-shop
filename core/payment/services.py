from django.core.exceptions import ValidationError
from django.db import transaction

from order.models import Order, OrderStatus

from .gateways.zarinpal import ZarinPalGateway
from .models import Payment, PaymentGateway, PaymentStatus


class PaymentService:

    @staticmethod
    def get_gateway(gateway):
        if gateway == PaymentGateway.ZARINPAL:
            return ZarinPalGateway()

        raise ValidationError(
            f"درگاه پرداخت «{gateway}» پشتیبانی نمی‌شود."
        )

    @staticmethod
    @transaction.atomic
    def create_payment(*, user, order, callback_url):
        """
        ساخت Payment و ارسال درخواست پرداخت به درگاه.
        """

        # -------------------------
        # بررسی کاربر
        # -------------------------

        if not user or not user.is_authenticated:
            raise ValidationError(
                "کاربر احراز هویت نشده است."
            )

        # -------------------------
        # بررسی مالکیت سفارش
        # -------------------------

        if order.user_id != user.id:
            raise ValidationError(
                "این سفارش متعلق به شما نیست."
            )

        # -------------------------
        # بررسی وضعیت سفارش
        # -------------------------

        if order.status != OrderStatus.PENDING:
            raise ValidationError(
                "این سفارش در وضعیت قابل پرداخت نیست."
            )

        # -------------------------
        # بررسی مبلغ
        # -------------------------

        if order.payable_amount <= 0:
            raise ValidationError(
                "مبلغ قابل پرداخت سفارش معتبر نیست."
            )

        # -------------------------
        # اگر پرداخت Pending قبلی وجود دارد
        # -------------------------

        existing_payment = (
            Payment.objects
            .filter(
                order=order,
                status=PaymentStatus.PENDING,
            )
            .order_by("-created_date")
            .first()
        )

        if existing_payment and existing_payment.authority:
            gateway = PaymentService.get_gateway(
                existing_payment.gateway
            )

            return {
                "payment": existing_payment,
                "payment_url": gateway.get_payment_url(
                    existing_payment.authority
                ),
                "is_new": False,
            }

        # -------------------------
        # ساخت Payment
        # -------------------------

        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=order.payable_amount,
            currency="IRR",
            gateway=PaymentGateway.ZARINPAL,
            status=PaymentStatus.PENDING,
        )

        # -------------------------
        # انتخاب Gateway
        # -------------------------

        gateway = PaymentService.get_gateway(
            payment.gateway
        )

        # -------------------------
        # Request به درگاه
        # -------------------------

        result = gateway.request_payment(
            payment=payment,
            callback_url=callback_url,
        )

        # -------------------------
        # اگر Request شکست خورد
        # -------------------------

        if not result["success"]:

            payment.status = PaymentStatus.FAILED
            payment.error_code = result.get(
                "error_code"
            )
            payment.error_message = result.get(
                "error_message"
            )
            payment.gateway_data = result.get(
                "raw_response",
                {},
            )

            payment.save(
                update_fields=[
                    "status",
                    "error_code",
                    "error_message",
                    "gateway_data",
                    "updated_date",
                ]
            )

            raise ValidationError(
                result.get(
                    "error_message",
                    "خطا در ایجاد پرداخت.",
                )
            )

        # -------------------------
        # ذخیره Authority
        # -------------------------

        payment.authority = result["authority"]

        payment.gateway_data = result.get(
            "raw_response",
            {},
        )

        payment.save(
            update_fields=[
                "authority",
                "gateway_data",
                "updated_date",
            ]
        )

        return {
            "payment": payment,
            "payment_url": result["payment_url"],
            "is_new": True,
        }

    @staticmethod
    @transaction.atomic
    def verify_payment(*, payment):
        """
        Verify پرداخت از طریق Gateway.
        """

        # -------------------------
        # اگر قبلاً موفق شده
        # -------------------------

        if payment.status == PaymentStatus.SUCCESS:
            return {
                "success": True,
                "payment": payment,
                "already_verified": True,
                "ref_id": payment.reference_id,
            }

        # -------------------------
        # Payment باید Pending باشد
        # -------------------------

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError(
                "این پرداخت قابل Verify نیست."
            )

        # -------------------------
        # Authority
        # -------------------------

        if not payment.authority:
            raise ValidationError(
                "Authority برای این پرداخت وجود ندارد."
            )

        # -------------------------
        # Gateway
        # -------------------------

        gateway = PaymentService.get_gateway(
            payment.gateway
        )

        # -------------------------
        # Verify
        # -------------------------

        result = gateway.verify_payment(
            payment=payment
        )

        # -------------------------
        # پرداخت ناموفق
        # -------------------------

        if not result["success"]:

            payment.status = PaymentStatus.FAILED

            payment.error_code = result.get(
                "error_code"
            )

            payment.error_message = result.get(
                "error_message"
            )

            payment.gateway_data = result.get(
                "raw_response",
                {},
            )

            payment.save(
                update_fields=[
                    "status",
                    "error_code",
                    "error_message",
                    "gateway_data",
                    "updated_date",
                ]
            )

            return {
                "success": False,
                "payment": payment,
                "already_verified": False,
                "error_code": result.get(
                    "error_code"
                ),
                "error_message": result.get(
                    "error_message"
                ),
            }

        # -------------------------
        # پرداخت موفق
        # -------------------------

        payment.status = PaymentStatus.SUCCESS

        payment.reference_id = result.get(
            "ref_id"
        )

        payment.gateway_data = result.get(
            "raw_response",
            {},
        )

        payment.error_code = None
        payment.error_message = None

        payment.save(
            update_fields=[
                "status",
                "reference_id",
                "gateway_data",
                "error_code",
                "error_message",
                "updated_date",
            ]
        )

        # -------------------------
        # نهایی کردن Order
        # -------------------------

        from order.services import OrderService

        order = OrderService.finalize_order(
            order_id=payment.order_id
        )

        return {
            "success": True,
            "payment": payment,
            "order": order,
            "already_verified": False,
            "ref_id": payment.reference_id,
        }