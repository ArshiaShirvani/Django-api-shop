from rest_framework import serializers

from order.models import Order

from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):

    order_id = serializers.IntegerField(
        help_text="شناسه سفارش"
    )

    def validate_order_id(self, value):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "کاربر احراز هویت نشده است."
            )

        try:
            order = Order.objects.get(
                id=value,
                user=request.user,
            )
        except Order.DoesNotExist:
            raise serializers.ValidationError(
                "سفارش مورد نظر پیدا نشد."
            )

        if order.status != "pending":
            raise serializers.ValidationError(
                "این سفارش در وضعیت قابل پرداخت نیست."
            )

        if order.payable_amount <= 0:
            raise serializers.ValidationError(
                "مبلغ قابل پرداخت سفارش معتبر نیست."
            )

        return value


class PaymentSerializer(serializers.ModelSerializer):

    order_tracking_code = serializers.CharField(
        source="order.tracking_code",
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
            "amount",
            "currency",
            "gateway",
            "status",
            "authority",
            "reference_id",
            "is_success",
            "created_date",
            "updated_date",
        )

        read_only_fields = fields