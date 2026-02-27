from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import PaymentModel, PaymentStatusType
from .zarinpal_clients import ZarinPalSandbox
from order.models import OrderModel, OrderStatusType
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404

class PaymentRequestApiView(APIView):

    def post(self, request, order_id):
        user = request.user

        order = get_object_or_404(
            OrderModel,
            id=order_id,
            user=user,
            status=OrderStatusType.PENDING.value
        )

        # جلوگیری از پرداخت تکراری
        if hasattr(order, "payment"):
            if order.payment.status == PaymentStatusType.SUCCESS.value:
                return Response(
                    {"error": "این سفارش قبلا پرداخت شده"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        amount = int(order.total_price) * 10  # تومان → ریال

        zarinpal = ZarinPalSandbox(
            merchant=settings.ZARINPAL_MERCHANT_ID,
            amount=amount
        )

        authority = zarinpal.payment_request(
            description=f"پرداخت سفارش {order.id}"
        )

        payment = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.total_price
        )

        order.payment = payment
        order.save()

        return Response({
            "payment_url": zarinpal.generate_payment_url(authority),
            "authority": authority
        })
        

from django.db import transaction
from django.shortcuts import redirect
from payment.models import PaymentModel, PaymentStatusType
from order.models import OrderModel


class PaymentVerifyApiView(APIView):

    def get(self, request):
        authority = request.GET.get("Authority")
        status = request.GET.get("Status")

        try:
            payment_obj = PaymentModel.objects.get(authority_id=authority)
        except PaymentModel.DoesNotExist:
            return Response({"error": "payment not found"}, status=404)

        if status != "OK":
            payment_obj.status = PaymentStatusType.FAILED
            payment_obj.save()
            return redirect("order:order-failed")

        order = payment_obj.order  # ← از related_name استفاده کن

        zp = ZarinPalSandbox(settings.ZARINPAL_MERCHANT_ID, payment_obj.amount)
        result = zp.payment_verify(payment_obj.amount, authority)

        if result["code"] == 100:
            with transaction.atomic():
                payment_obj.ref_id = result["ref_id"]
                payment_obj.status = PaymentStatusType.SUCCESS
                payment_obj.response_json = result
                payment_obj.save()

                order.status = "paid"
                order.save()

                # کاهش موجودی
                for item in order.order_items.all():
                    variant = item.variant
                    if variant.stock < item.quantity:
                        raise Exception("stock error")
                    variant.stock -= item.quantity
                    variant.save()

                # منقضی کردن کد تخفیف
                if order.coupon:
                    order.coupon.is_active = False
                    order.coupon.save()

            return redirect("order:order-success")

        payment_obj.status = PaymentStatusType.FAILED
        payment_obj.save()
        return redirect("order:order-failed")