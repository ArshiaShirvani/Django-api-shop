from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "user",
        "amount",
        "currency",
        "gateway",
        "status",
        "authority",
        "reference_id",
        "created_date",
    )

    list_filter = (
        "status",
        "gateway",
        "currency",
        "created_date",
    )

    search_fields = (
        "authority",
        "reference_id",
        "order__tracking_code",
        "user__phone_number",
    )

    readonly_fields = (
        "order",
        "user",
        "amount",
        "currency",
        "gateway",
        "status",
        "authority",
        "reference_id",
        "gateway_data",
        "error_code",
        "error_message",
        "created_date",
        "updated_date",
    )

    autocomplete_fields = (
        "order",
        "user",
    )

    ordering = (
        "-created_date",
    )

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات پرداخت",
            {
                "fields": (
                    "order",
                    "user",
                    "amount",
                    "currency",
                    "gateway",
                    "status",
                )
            },
        ),
        (
            "اطلاعات درگاه",
            {
                "fields": (
                    "authority",
                    "reference_id",
                    "gateway_data",
                )
            },
        ),
        (
            "خطا",
            {
                "fields": (
                    "error_code",
                    "error_message",
                )
            },
        ),
        (
            "تاریخ‌ها",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            },
        ),
    )