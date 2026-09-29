from rest_framework import serializers

from order.models import (
    Order,
    OrderItem,
    OrderStatus,
)


# =========================================================
# ORDER ITEM DETAIL
# =========================================================

class AdminOrderItemDetailSerializer(
    serializers.ModelSerializer
):

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
        )


# =========================================================
# ORDER LIST
# =========================================================

class AdminOrderListSerializer(serializers.ModelSerializer):

    customer_name = serializers.SerializerMethodField()

    customer_phone = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    payment_status = serializers.SerializerMethodField()

    shipping_method_title = serializers.CharField(
        source="shipping_method.title",
        read_only=True,
    )

    payable_amount = serializers.IntegerField(
        read_only=True,
    )

    class Meta:

        model = Order

        fields = (
            "id",
            "tracking_code",

            "customer_name",
            "customer_phone",

            "status",
            "payment_status",

            "subtotal",
            "discount",
            "tax",
            "shipping_cost",
            "total",
            "payable_amount",

            "shipping_method_title",

            "created_date",
        )

    def get_customer_name(self, obj):

        return obj.recipient_name

    def get_payment_status(self, obj):

        if obj.is_paid:
            return "paid"

        return "pending"


# =========================================================
# ORDER DETAIL
# =========================================================

class AdminOrderDetailSerializer(
    serializers.ModelSerializer
):

    payment_status = serializers.SerializerMethodField()

    customer = serializers.SerializerMethodField()

    address = serializers.SerializerMethodField()

    items = AdminOrderItemDetailSerializer(
        many=True,
        read_only=True,
    )

    prices = serializers.SerializerMethodField()

    coupon = serializers.SerializerMethodField()

    shipping_method = serializers.SerializerMethodField()

    payable_amount = serializers.IntegerField(
        read_only=True,
    )

    class Meta:

        model = Order

        fields = (
            "id",
            "tracking_code",
            "status",
            "payment_status",

            "customer",
            "address",

            "items",

            "prices",

            "coupon",

            "shipping_method",

            "payable_amount",

            "created_date",
            "updated_date",
        )

    # =====================================================
    # PAYMENT STATUS
    # =====================================================

    def get_payment_status(self, obj):

        if obj.is_paid:
            return "paid"

        return "pending"

    # =====================================================
    # CUSTOMER
    # =====================================================

    def get_customer(self, obj):

        return {
            "user_id": obj.user_id,
            "phone_number": obj.user.phone_number,
            "recipient_name": obj.recipient_name,
        }

    # =====================================================
    # ADDRESS
    # =====================================================

    def get_address(self, obj):

        return {
            "recipient_name": obj.recipient_name,
            "recipient_phone": obj.recipient_phone,
            "province": obj.province,
            "city": obj.city,
            "address": obj.address,
            "postal_code": obj.postal_code,
            "plaque": obj.plaque,
            "unit": obj.unit,
        }

    # =====================================================
    # PRICES
    # =====================================================

    def get_prices(self, obj):

        return {
            "subtotal": obj.subtotal,
            "discount": obj.discount,
            "tax": obj.tax,
            "shipping_cost": obj.shipping_cost,
            "total": obj.total,
            "payable_amount": obj.payable_amount,
        }

    # =====================================================
    # COUPON
    # =====================================================

    def get_coupon(self, obj):

        if not obj.coupon:
            return None

        return {
            "id": obj.coupon.id,
            "code": obj.coupon.code,
            "discount_type": obj.coupon.discount_type,
            "discount_value": obj.coupon.discount_value,
        }

    # =====================================================
    # SHIPPING METHOD
    # =====================================================

    def get_shipping_method(self, obj):

        if not obj.shipping_method:
            return None

        return {
            "id": obj.shipping_method.id,
            "title": obj.shipping_method.title,
            "code": obj.shipping_method.code,
            "description": obj.shipping_method.description,
        }


# =========================================================
# ORDER STATUS UPDATE
# =========================================================

class AdminOrderStatusUpdateSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=OrderStatus.choices,
        required=True,
    )