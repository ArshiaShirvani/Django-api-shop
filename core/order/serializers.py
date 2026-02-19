from rest_framework import serializers
from .models import (OrderModel,
                     OrderItemsModel,
                     OrderStatusType,
                     ShippingMethodType,
                     UserAddressModel,
                     CouponModel,
                     )
from shop.seralizers import ProductVariantSerilizer
from shop.models import ProductVariant
from django.db import transaction
from django.utils import timezone


class CouponApplySerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=10)
    
    def validate(self, attrs):
        user = self.context["request"].user
        code = attrs["code"]
        try:
            coupon = CouponModel.objects.filter(code=code,is_active=True)
        except CouponModel.DoesNotExist:
            raise serializers.ValidationError["کد تخفیف معتبر نیست"]
        
        if coupon.expiration_date < timezone.now():
            raise serializers.ValidationError("کد تخفیف منقضی شده است")
        if coupon.allowed_users.exists() and user not in coupon.allowed_users.all():
            raise serializers.ValidationError("شما مجاز به استفاده از این کد تخفیف نیستید")
        if user in coupon.used_by.all():
            raise serializers.ValidationError("این تخفیف قبلا استفاده شده است")
        
        
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        fields = [
            "user",
            "email",
            "address",
            "state",
            "city",
            "zip_code",
            "plate",
        ]
        read_only_fields = ["id","user","email"]
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerilizer(read_only=True)
    
    class Meta:
        model = OrderItemsModel
        fields = [
            "id",
            "order",
            "variant",
            "quantity",
            "price",
        ]
        
        
class OrderCreateItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderCreateItemSerializer(many=True)
    coupon_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = OrderModel
        fields = ["id", "address", "shipping_method", "coupon_code", "items"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = self.context["request"].user
        address = attrs["address"]

        if address.user != user:
            raise serializers.ValidationError("آدرس متعلق به کاربر نیست")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        items_data = validated_data.pop("items")
        coupon_code = validated_data.pop("coupon_code", None)

        coupon = None
        discount_percent = 0

        
        if coupon_code:
            coupon_serializer = CouponApplySerializer(
                data={"code": coupon_code},
                context=self.context
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

                
                if variant.stock < quantity:
                    raise serializers.ValidationError(
                        f"موجودی برای {variant} کافی نیست"
                    )

                price = variant.final_price

                OrderItemsModel.objects.create(
                    order=order,
                    variant=variant,
                    quantity=quantity,
                    price=price
                )

                
                variant.stock = F("stock") - quantity
                variant.save(update_fields=["stock"])

                total_price += price * quantity

            
            if discount_percent:
                total_price = total_price - (total_price * discount_percent // 100)

                coupon.used_by.add(user)

                
                if hasattr(coupon, "usage_limit") and coupon.usage_limit == 1:
                    coupon.is_active = False
                    coupon.save(update_fields=["is_active"])

            order.total_price = total_price
            order.save(update_fields=["total_price"])

        return order

    
    
class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True,read_only=True)
    address = UserAddressSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    shipping_display = serializers.CharField(source="get_shipping_method_display", read_only=True)
    
    class Meta:
        model = OrderModel
        fields = [
            "id",
            "address",
            "total_price",
            "tax_percent",
            "shipping_method",
            "shipping_display",
            "status",
            "status_display",
            "order_items",
            "created_date"
        ]