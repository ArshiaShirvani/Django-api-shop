from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.phone_number")

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_date",
            "updated_date",
        ]