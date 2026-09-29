from rest_framework import serializers

from review.models import Review


# =========================================================
# USER
# =========================================================

class AdminReviewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    phone_number = serializers.CharField(read_only=True)


# =========================================================
# PRODUCT
# =========================================================

class AdminReviewProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)


# =========================================================
# LIST
# =========================================================

class AdminReviewListSerializer(serializers.ModelSerializer):
    user = AdminReviewUserSerializer(read_only=True)
    product = AdminReviewProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "created_date",
            "updated_date",
        )


# =========================================================
# DETAIL
# =========================================================

class AdminReviewDetailSerializer(serializers.ModelSerializer):
    user = AdminReviewUserSerializer(read_only=True)
    product = AdminReviewProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "created_date",
            "updated_date",
        )


# =========================================================
# CREATE
# =========================================================

class AdminReviewCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = (
            "user_id",
            "product_id",
            "rating",
            "comment",
        )

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "امتیاز باید بین 1 تا 5 باشد."
            )

        return value

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        product_id = attrs.get("product_id")

        if Review.objects.filter(
            user_id=user_id,
            product_id=product_id,
        ).exists():
            raise serializers.ValidationError(
                "این کاربر قبلاً برای این محصول نظر ثبت کرده است."
            )

        return attrs

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        product_id = validated_data.pop("product_id")

        return Review.objects.create(
            user_id=user_id,
            product_id=product_id,
            **validated_data,
        )


# =========================================================
# UPDATE
# =========================================================

class AdminReviewUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        write_only=True,
        required=False,
    )

    product_id = serializers.IntegerField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = Review
        fields = (
            "user_id",
            "product_id",
            "rating",
            "comment",
        )

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "امتیاز باید بین 1 تا 5 باشد."
            )

        return value

    def validate(self, attrs):
        user_id = attrs.get(
            "user_id",
            self.instance.user_id,
        )

        product_id = attrs.get(
            "product_id",
            self.instance.product_id,
        )

        duplicate = Review.objects.filter(
            user_id=user_id,
            product_id=product_id,
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if duplicate:
            raise serializers.ValidationError(
                "این کاربر قبلاً برای این محصول نظر ثبت کرده است."
            )

        return attrs

    def update(self, instance, validated_data):
        if "user_id" in validated_data:
            instance.user_id = validated_data.pop("user_id")

        if "product_id" in validated_data:
            instance.product_id = validated_data.pop("product_id")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance