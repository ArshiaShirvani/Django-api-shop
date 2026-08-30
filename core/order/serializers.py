from rest_framework import serializers

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    Order,
    OrderItem,
)


# =========================================================
# Address
# =========================================================

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = [
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
        ]

        read_only_fields = [
            "id",
            "created_date",
            "updated_date",
        ]

    def validate_recipient_phone(self, value):

        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "شماره تماس فقط باید شامل عدد باشد."
            )

        if len(value) != 11:
            raise serializers.ValidationError(
                "شماره تماس باید ۱۱ رقم باشد."
            )

        if not value.startswith("09"):
            raise serializers.ValidationError(
                "شماره تماس معتبر نیست."
            )

        return value

    def validate_postal_code(self, value):

        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "کد پستی فقط باید شامل عدد باشد."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "کد پستی باید ۱۰ رقم باشد."
            )

        return value

    def validate(self, attrs):

        if self.instance is None:

            required_fields = [
                "title",
                "recipient_name",
                "recipient_phone",
                "province",
                "city",
                "address",
                "postal_code",
            ]

            for field in required_fields:

                value = attrs.get(field)

                if value is None or not str(value).strip():

                    raise serializers.ValidationError({
                        field: "این فیلد الزامی است."
                    })

        return attrs


# =========================================================
# Shipping Method
# =========================================================

class ShippingMethodSerializer(
    serializers.ModelSerializer
):

    calculated_cost = serializers.SerializerMethodField()

    class Meta:
        model = ShippingMethod

        fields = [
            "id",
            "title",
            "code",
            "description",
            "base_cost",
            "free_shipping_minimum",
            "calculated_cost",
            "display_order",
        ]

        read_only_fields = [
            "id",
            "calculated_cost",
        ]

    def get_calculated_cost(self, obj):

        subtotal = self.context.get(
            "subtotal",
            0,
        )

        return obj.calculate_cost(
            subtotal
        )


# =========================================================
# Order Shipping Method
# =========================================================

class OrderShippingMethodSerializer(
    serializers.ModelSerializer
):

    cost = serializers.SerializerMethodField()

    class Meta:
        model = ShippingMethod

        fields = [
            "id",
            "title",
            "code",
            "description",
            "cost",
        ]

        read_only_fields = fields

    def get_cost(self, obj):

        order = self.context.get(
            "order"
        )

        if not order:
            return 0

        return order.shipping_cost


# =========================================================
# Coupon Apply
# =========================================================

class CouponApplySerializer(
    serializers.Serializer
):

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


# =========================================================
# Order Item
# =========================================================

class OrderItemSerializer(
    serializers.ModelSerializer
):

    product_id = serializers.IntegerField(
        source="variant.product.id",
        read_only=True,
    )

    product_slug = serializers.CharField(
        source="variant.product.slug",
        read_only=True,
    )

    image = serializers.SerializerMethodField()

    line_total = serializers.IntegerField(
        source="subtotal",
        read_only=True,
    )

    class Meta:
        model = OrderItem

        fields = [
            "id",

            # Product
            "product_id",
            "product_slug",
            "product_title",
            "image",

            # Variant
            "sku",
            "size",
            "color",
            "color_code",

            # Price
            "original_unit_price",
            "discount_percent",
            "unit_price",

            # Quantity
            "quantity",

            # Total
            "subtotal",
            "line_total",

            "created_date",
        ]

        read_only_fields = fields

    def get_image(self, obj):

        product = obj.variant.product

        image = (
            product.images
            .filter(
                is_main=True
            )
            .first()
        )

        if not image:

            image = (
                product.images
                .order_by("id")
                .first()
            )

        if not image:
            return None

        request = self.context.get(
            "request"
        )

        if request:

            return request.build_absolute_uri(
                image.image.url
            )

        return image.image.url


# =========================================================
# Order List
# =========================================================

class OrderListSerializer(
    serializers.ModelSerializer
):

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    items_count = serializers.IntegerField(
        read_only=True,
    )

    shipping_method_title = serializers.CharField(
        source="shipping_title",
        read_only=True,
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",

            "status",
            "status_display",

            "items_count",

            "subtotal",
            "discount_amount",
            "shipping_cost",
            "total_price",

            "coupon_code",

            "shipping_method_title",

            "created_date",
            "paid_at",
            "shipped_at",
            "delivered_at",
            "cancelled_at",
        ]

        read_only_fields = fields


# =========================================================
# Order Detail
# =========================================================

class OrderDetailSerializer(
    serializers.ModelSerializer
):

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    shipping_method = serializers.SerializerMethodField()

    is_paid = serializers.BooleanField(
        read_only=True,
    )

    is_cancelled = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Order

        fields = [

            # Basic
            "id",
            "order_number",

            "status",
            "status_display",

            "is_paid",
            "is_cancelled",

            # Items
            "items",

            # Coupon
            "coupon_code",
            "coupon_discount",

            # Shipping
            "shipping_method",
            "shipping_title",
            "shipping_cost",

            "tracking_code",

            # Address
            "recipient_name",
            "recipient_phone",

            "province",
            "city",
            "address",
            "postal_code",

            "plaque",
            "unit",

            # Price
            "subtotal",
            "discount_amount",
            "total_price",

            # Payment
            "payment_reference",

            # Dates
            "paid_at",
            "shipped_at",
            "delivered_at",
            "cancelled_at",

            "created_date",
            "updated_date",
        ]

        read_only_fields = fields

    def get_shipping_method(self, obj):

        if not obj.shipping_method:
            return None

        return {
            "id": obj.shipping_method.id,
            "title": obj.shipping_method.title,
            "code": obj.shipping_method.code,
            "description": obj.shipping_method.description,
            "cost": obj.shipping_cost,
        }


# =========================================================
# Create Order
# =========================================================

class CreateOrderSerializer(
    serializers.Serializer
):

    address_id = serializers.IntegerField(
        min_value=1
    )

    shipping_method_id = serializers.IntegerField(
        min_value=1
    )

    coupon_code = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate_coupon_code(self, value):

        if not value:
            return None

        return value.strip().upper()

    def validate(self, attrs):

        request = self.context.get(
            "request"
        )

        if not request:

            raise serializers.ValidationError(
                "درخواست نامعتبر است."
            )

        if not request.user.is_authenticated:

            raise serializers.ValidationError(
                "برای ثبت سفارش باید وارد حساب کاربری شوید."
            )

        return attrs