from rest_framework import serializers

from order.models import ShippingMethod


# =========================================================
# LIST
# =========================================================

class AdminShippingMethodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = (
            "id",
            "title",
            "code",
            "base_cost",
            "free_shipping_minimum",
            "is_active",
            "display_order",
            "created_date",
            "updated_date",
        )


# =========================================================
# DETAIL
# =========================================================

class AdminShippingMethodDetailSerializer(serializers.ModelSerializer):
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
            "created_date",
            "updated_date",
        )


# =========================================================
# CREATE
# =========================================================

class AdminShippingMethodCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = (
            "title",
            "code",
            "description",
            "base_cost",
            "free_shipping_minimum",
            "is_active",
            "display_order",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "عنوان روش ارسال نمی‌تواند خالی باشد."
            )

        return value

    def validate_code(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "کد روش ارسال نمی‌تواند خالی باشد."
            )

        return value

    def validate_base_cost(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "هزینه ارسال نمی‌تواند منفی باشد."
            )

        return value

    def validate_free_shipping_minimum(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "حداقل مبلغ ارسال رایگان نمی‌تواند منفی باشد."
            )

        return value

    def validate_display_order(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "ترتیب نمایش نمی‌تواند منفی باشد."
            )

        return value


# =========================================================
# UPDATE
# =========================================================

class AdminShippingMethodUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = (
            "title",
            "code",
            "description",
            "base_cost",
            "free_shipping_minimum",
            "is_active",
            "display_order",
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "عنوان روش ارسال نمی‌تواند خالی باشد."
            )

        return value

    def validate_code(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "کد روش ارسال نمی‌تواند خالی باشد."
            )

        return value

    def validate_base_cost(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "هزینه ارسال نمی‌تواند منفی باشد."
            )

        return value

    def validate_free_shipping_minimum(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "حداقل مبلغ ارسال رایگان نمی‌تواند منفی باشد."
            )

        return value

    def validate_display_order(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "ترتیب نمایش نمی‌تواند منفی باشد."
            )

        return value