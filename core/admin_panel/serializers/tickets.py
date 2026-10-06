from rest_framework import serializers

from website.models import ContactMessage


# =========================================================
# TICKET LIST
# =========================================================

class AdminTicketListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactMessage

        fields = (
            "id",
            "name",
            "subject",
            "phone",
            "email",
            "seen",
            "created_date",
        )

        read_only_fields = (
            "id",
            "name",
            "subject",
            "phone",
            "email",
            "created_date",
        )


# =========================================================
# TICKET DETAIL
# =========================================================

class AdminTicketDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactMessage

        fields = (
            "id",
            "name",
            "subject",
            "phone",
            "email",
            "message",
            "seen",
            "created_date",
        )

        read_only_fields = (
            "id",
            "name",
            "subject",
            "phone",
            "email",
            "message",
            "created_date",
        )