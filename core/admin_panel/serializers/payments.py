from rest_framework import serializers

from payment.models import Payment


# =========================================================
# PAYMENT LIST
# =========================================================

class AdminPaymentListSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="order.recipient_name",
        read_only=True,
    )

    customer_phone = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    order_tracking_code = serializers.CharField(
        source="order.tracking_code",
        read_only=True,
    )

    order_status = serializers.CharField(
        source="order.status",
        read_only=True,
    )

    is_success = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Payment

        fields = (
            "id",
            "order",
            "order_tracking_code",
            "order_status",
            "customer_name",
            "customer_phone",
            "amount",
            "currency",
            "gateway",
            "status",
            "authority",
            "reference_id",
            "is_success",
            "created_date",
        )


# =========================================================
# PAYMENT DETAIL
# =========================================================

class AdminPaymentDetailSerializer(serializers.ModelSerializer):

    customer = serializers.SerializerMethodField()

    order = serializers.SerializerMethodField()

    is_success = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Payment

        fields = (
            "id",
            "customer",
            "order",
            "amount",
            "currency",
            "gateway",
            "status",
            "authority",
            "reference_id",
            "gateway_data",
            "error_code",
            "error_message",
            "is_success",
            "created_date",
            "updated_date",
        )

    def get_customer(self, obj):
        return {
            "user_id": obj.user_id,
            "phone_number": obj.user.phone_number,
            "recipient_name": obj.order.recipient_name,
        }

    def get_order(self, obj):
        return {
            "id": obj.order_id,
            "tracking_code": obj.order.tracking_code,
            "status": obj.order.status,
            "subtotal": obj.order.subtotal,
            "discount": obj.order.discount,
            "tax": obj.order.tax,
            "shipping_cost": obj.order.shipping_cost,
            "total": obj.order.total,
            "payable_amount": obj.order.payable_amount,
            "created_date": obj.order.created_date,
        }