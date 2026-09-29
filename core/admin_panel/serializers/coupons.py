from rest_framework import serializers

from order.models import (
    Coupon,
    CouponUsage,
)


# =========================================================
# COUPON USER
# =========================================================

class AdminCouponUserSerializer(serializers.Serializer):

    id = serializers.IntegerField(
        read_only=True,
    )

    phone_number = serializers.CharField(
        read_only=True,
    )


# =========================================================
# COUPON LIST
# =========================================================

class AdminCouponListSerializer(serializers.ModelSerializer):

    usage_count = serializers.SerializerMethodField()

    is_valid_time = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Coupon

        fields = (
            "id",
            "code",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "minimum_order_amount",
            "usage_limit",
            "usage_limit_per_user",
            "usage_count",
            "is_global",
            "is_active",
            "is_valid_time",
            "start_date",
            "end_date",
            "created_date",
            "updated_date",
        )

    def get_usage_count(self, obj):
        return obj.usages.count()


# =========================================================
# COUPON DETAIL
# =========================================================

class AdminCouponDetailSerializer(serializers.ModelSerializer):

    usage_count = serializers.SerializerMethodField()

    is_valid_time = serializers.BooleanField(
        read_only=True,
    )

    users = AdminCouponUserSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Coupon

        fields = (
            "id",
            "code",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "minimum_order_amount",
            "start_date",
            "end_date",
            "usage_limit",
            "usage_limit_per_user",
            "is_global",
            "users",
            "is_active",
            "usage_count",
            "is_valid_time",
            "created_date",
            "updated_date",
        )

    def get_usage_count(self, obj):
        return obj.usages.count()


# =========================================================
# COUPON CREATE
# =========================================================

class AdminCouponCreateSerializer(serializers.ModelSerializer):

    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Coupon.users.rel.related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = Coupon

        fields = (
            "code",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "minimum_order_amount",
            "start_date",
            "end_date",
            "usage_limit",
            "usage_limit_per_user",
            "is_global",
            "users",
            "is_active",
        )

    def validate_code(self, value):

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "کد تخفیف نمی‌تواند خالی باشد."
            )

        return value

    def validate(self, attrs):

        discount_type = attrs.get(
            "discount_type"
        )

        discount_value = attrs.get(
            "discount_value"
        )

        max_discount_amount = attrs.get(
            "max_discount_amount"
        )

        start_date = attrs.get(
            "start_date"
        )

        end_date = attrs.get(
            "end_date"
        )

        is_global = attrs.get(
            "is_global",
            True,
        )

        users = attrs.get(
            "users",
            [],
        )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        if start_date and end_date:

            if start_date >= end_date:

                raise serializers.ValidationError(
                    {
                        "end_date": (
                            "تاریخ پایان باید بعد از تاریخ شروع باشد."
                        )
                    }
                )

        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        if discount_type == Coupon.DiscountType.PERCENTAGE:

            if discount_value > 100:

                raise serializers.ValidationError(
                    {
                        "discount_value": (
                            "درصد تخفیف نمی‌تواند بیشتر از 100 باشد."
                        )
                    }
                )

        # -------------------------------------------------
        # FIXED
        # -------------------------------------------------

        if discount_type == Coupon.DiscountType.FIXED:

            if max_discount_amount is not None:

                raise serializers.ValidationError(
                    {
                        "max_discount_amount": (
                            "حداکثر مبلغ تخفیف فقط برای "
                            "تخفیف درصدی قابل استفاده است."
                        )
                    }
                )

        # -------------------------------------------------
        # GLOBAL / SPECIFIC USERS
        # -------------------------------------------------

        if not is_global and not users:

            raise serializers.ValidationError(
                {
                    "users": (
                        "برای کد تخفیف اختصاصی باید حداقل "
                        "یک کاربر انتخاب شود."
                    )
                }
            )

        return attrs

    def create(self, validated_data):

        users = validated_data.pop(
            "users",
            [],
        )

        coupon = Coupon.objects.create(
            **validated_data
        )

        if users:
            coupon.users.set(users)

        return coupon


# =========================================================
# COUPON UPDATE
# =========================================================

class AdminCouponUpdateSerializer(serializers.ModelSerializer):

    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Coupon.users.rel.related_model.objects.all(),
        required=False,
    )

    class Meta:
        model = Coupon

        fields = (
            "code",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "minimum_order_amount",
            "start_date",
            "end_date",
            "usage_limit",
            "usage_limit_per_user",
            "is_global",
            "users",
            "is_active",
        )

    def validate_code(self, value):

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "کد تخفیف نمی‌تواند خالی باشد."
            )

        return value

    def validate(self, attrs):

        discount_type = attrs.get(
            "discount_type",
            getattr(
                self.instance,
                "discount_type",
                None,
            ),
        )

        discount_value = attrs.get(
            "discount_value",
            getattr(
                self.instance,
                "discount_value",
                None,
            ),
        )

        max_discount_amount = attrs.get(
            "max_discount_amount",
            getattr(
                self.instance,
                "max_discount_amount",
                None,
            ),
        )

        start_date = attrs.get(
            "start_date",
            getattr(
                self.instance,
                "start_date",
                None,
            ),
        )

        end_date = attrs.get(
            "end_date",
            getattr(
                self.instance,
                "end_date",
                None,
            ),
        )

        is_global = attrs.get(
            "is_global",
            getattr(
                self.instance,
                "is_global",
                True,
            ),
        )

        users = attrs.get(
            "users",
            None,
        )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        if start_date and end_date:

            if start_date >= end_date:

                raise serializers.ValidationError(
                    {
                        "end_date": (
                            "تاریخ پایان باید بعد از تاریخ شروع باشد."
                        )
                    }
                )

        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        if discount_type == Coupon.DiscountType.PERCENTAGE:

            if discount_value > 100:

                raise serializers.ValidationError(
                    {
                        "discount_value": (
                            "درصد تخفیف نمی‌تواند بیشتر از 100 باشد."
                        )
                    }
                )

        # -------------------------------------------------
        # FIXED
        # -------------------------------------------------

        if discount_type == Coupon.DiscountType.FIXED:

            if max_discount_amount is not None:

                raise serializers.ValidationError(
                    {
                        "max_discount_amount": (
                            "حداکثر مبلغ تخفیف فقط برای "
                            "تخفیف درصدی قابل استفاده است."
                        )
                    }
                )

        # -------------------------------------------------
        # SPECIFIC USERS
        # -------------------------------------------------

        if not is_global:

            if users is not None and not users:

                raise serializers.ValidationError(
                    {
                        "users": (
                            "برای کد تخفیف اختصاصی باید حداقل "
                            "یک کاربر انتخاب شود."
                        )
                    }
                )

            if users is None:

                if not self.instance.users.exists():

                    raise serializers.ValidationError(
                        {
                            "users": (
                                "برای کد تخفیف اختصاصی باید حداقل "
                                "یک کاربر انتخاب شود."
                            )
                        }
                    )

        return attrs

    def update(self, instance, validated_data):

        users = validated_data.pop(
            "users",
            None,
        )

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value,
            )

        instance.save()

        if users is not None:
            instance.users.set(users)

        return instance


# =========================================================
# COUPON USAGE
# =========================================================

class AdminCouponUsageSerializer(serializers.ModelSerializer):

    coupon_code = serializers.CharField(
        source="coupon.code",
        read_only=True,
    )

    user_phone = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    order_tracking_code = serializers.CharField(
        source="order.tracking_code",
        read_only=True,
    )

    class Meta:
        model = CouponUsage

        fields = (
            "id",
            "coupon",
            "coupon_code",
            "user",
            "user_phone",
            "order",
            "order_tracking_code",
            "used_date",
        )

        read_only_fields = fields