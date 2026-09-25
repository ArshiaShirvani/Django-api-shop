from rest_framework import serializers


# =========================================================
# USER LIST
# =========================================================

class AdminUserListSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    phone_number = serializers.CharField()

    first_name = serializers.CharField(
        allow_null=True,
        required=False
    )

    last_name = serializers.CharField(
        allow_null=True,
        required=False
    )

    role = serializers.CharField()

    is_active = serializers.BooleanField()

    is_verified = serializers.BooleanField()

    created_date = serializers.DateTimeField()


# =========================================================
# USER DETAIL
# =========================================================

class AdminUserDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    phone_number = serializers.CharField()

    first_name = serializers.CharField(
        allow_null=True,
        required=False
    )

    last_name = serializers.CharField(
        allow_null=True,
        required=False
    )

    role = serializers.CharField()

    is_active = serializers.BooleanField()

    is_verified = serializers.BooleanField()

    created_date = serializers.DateTimeField()

    orders_count = serializers.IntegerField()

    total_purchases = serializers.IntegerField()


# =========================================================
# USER STATUS
# =========================================================

class AdminUserStatusSerializer(serializers.Serializer):

    is_active = serializers.BooleanField()