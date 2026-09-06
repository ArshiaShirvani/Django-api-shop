from rest_framework import serializers

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    Order,
    OrderItem,
)


# =========================================================
# ADDRESS
# =========================================================

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = (
            "id",
            "title",
            "recipient_name",
            "recipient_phone",
            "province",
            "city",
            "address",
            "postal_code",
            "plaque",
            "unit",
            "is_default",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
        )

    def validate(self, attrs):

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            recipient_name = attrs.get(
                "recipient_name",
                getattr(self.instance, "recipient_name", None),
            )

            recipient_phone = attrs.get(
                "recipient_phone",
                getattr(self.instance, "recipient_phone", None),
            )

            if not recipient_name:
                raise serializers.ValidationError({
                    "recipient_name": "نام گیرنده الزامی است."
                })

            if not recipient_phone:
                raise serializers.ValidationError({
                    "recipient_phone": "شماره تماس گیرنده الزامی است."
                })

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        return Address.objects.create(
            user=request.user,
            **validated_data
        )


# =========================================================
# SHIPPING METHOD
# =========================================================

class ShippingMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingMethod

        fields = (
            "id",
            "title",
            "code",
            "description",
            "base_cost",
            "free_shipping_minimum",
            "is_active",
            "display_order",
        )

        read_only_fields = fields


# =========================================================
# COUPON APPLY
# =========================================================

class CouponApplySerializer(serializers.Serializer):

    code = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
    )

    def validate_code(self, value):

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "کد تخفیف را وارد کنید."
            )

        return value

    def validate(self, attrs):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "کاربر احراز هویت نشده است."
            )

        try:
            coupon = Coupon.objects.get(
                code=attrs["code"]
            )
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({
                "code": "کد تخفیف معتبر نیست."
            })

        if not coupon.is_available_for_user(request.user):
            raise serializers.ValidationError({
                "code": "این کد تخفیف برای شما قابل استفاده نیست."
            })

        attrs["coupon"] = coupon

        return attrs


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItemSerializer(serializers.ModelSerializer):

    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem

        fields = (
            "id",
            "product_title",
            "size",
            "color",
            "sku",
            "unit_price",
            "quantity",
            "subtotal",
            "final_price",
        )

        read_only_fields = fields

    def get_final_price(self, obj):

        return obj.unit_price


# =========================================================
# ORDER
# =========================================================

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    shipping_method_title = serializers.CharField(
        source="shipping_method.title",
        read_only=True,
    )

    coupon_code_display = serializers.CharField(
        source="coupon.code",
        read_only=True,
    )

    payable_amount = serializers.IntegerField(
        read_only=True,
    )

    is_paid = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Order

        fields = (
            "id",
            "tracking_code",
            "status",

            # prices
            "subtotal",
            "discount",
            "tax",
            "shipping_cost",
            "total",
            "payable_amount",

            # coupon
            "coupon_code_display",

            # shipping
            "shipping_method",
            "shipping_method_title",

            # address snapshot
            "recipient_name",
            "recipient_phone",
            "province",
            "city",
            "address",
            "postal_code",
            "plaque",
            "unit",

            # items
            "items",

            # status
            "is_paid",

            # dates
            "created_date",
            "updated_date",
        )

        read_only_fields = fields
        
class OrderCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(
        help_text="شناسه آدرس"
    )

    shipping_method_id = serializers.IntegerField(
        help_text="شناسه روش ارسال"
    )

    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="کد تخفیف - اختیاری"
    )