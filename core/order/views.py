from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.db.models import F

from .models import OrderModel, OrderItemsModel
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    CouponApplySerializer
)

from shop.models import ProductVariant


class OrderCreateApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        user = request.user

        items_data = validated_data.pop("items")
        coupon_code = validated_data.pop("coupon_code", None)

        coupon = None
        discount_percent = 0

        # validation of coupon
        if coupon_code:
            coupon_serializer = CouponApplySerializer(
                data={"code": coupon_code},
                context={"request": request}
            )
            coupon_serializer.is_valid(raise_exception=True)
            coupon = coupon_serializer.validated_data["coupon"]
            discount_percent = coupon.discount_percent

        with transaction.atomic():

            order = OrderModel.objects.create(
                user=user,
                coupon=coupon,
                **validated_data
            )

            total_price = 0

            for item in items_data:
                variant = ProductVariant.objects.select_for_update().get(
                    id=item["variant_id"],
                    is_active=True
                )

                quantity = item["quantity"]

                # perevent to oversell
                if variant.stock < quantity:
                    return Response(
                        {"error": f"موجودی برای {variant} کافی نیست"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                price = variant.final_price

                OrderItemsModel.objects.create(
                    order=order,
                    variant=variant,
                    quantity=quantity,
                    price=price
                )

                # reduce quantity
                variant.stock = F("stock") - quantity
                variant.save(update_fields=["stock"])

                total_price += price * quantity

            # submit coupon
            if discount_percent:
                total_price -= total_price * discount_percent // 100
                coupon.used_by.add(user)

                
                if hasattr(coupon, "usage_limit") and coupon.usage_limit == 1:
                    coupon.is_active = False
                    coupon.save(update_fields=["is_active"])

            order.total_price = total_price
            order.save(update_fields=["total_price"])

        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            order = OrderModel.objects.get(id=pk, user=request.user)
        except OrderModel.DoesNotExist:
            return Response(
                {"error": "سفارش یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(OrderDetailSerializer(order).data)


class UserOrdersListApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).order_by("-created_date")
        data = OrderDetailSerializer(orders, many=True).data
        return Response(data)
