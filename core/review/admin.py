from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_info",
        "product",
        "rating_display",
        "comment_preview",
        "created_date",
        "updated_date",
    )

    list_display_links = (
        "id",
        "product",
    )

    list_filter = (
        "rating",
        "created_date",
        "updated_date",
    )

    search_fields = (
        "comment",
        "user__phone_number",
        "product__title",
    )

    ordering = (
        "-created_date",
    )

    list_per_page = 25

    readonly_fields = (
        "created_date",
        "updated_date",
    )

    fieldsets = (
        (
            "اطلاعات نظر",
            {
                "fields": (
                    "user",
                    "product",
                    "rating",
                    "comment",
                )
            },
        ),
        (
            "اطلاعات زمانی",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            },
        ),
    )

    def user_info(self, obj):
        return obj.user.phone_number

    user_info.short_description = "کاربر"
    user_info.admin_order_field = "user__phone_number"

    def rating_display(self, obj):
        return f"{obj.rating} / 5"

    rating_display.short_description = "امتیاز"
    rating_display.admin_order_field = "rating"

    def comment_preview(self, obj):
        if len(obj.comment) > 60:
            return f"{obj.comment[:60]}..."
        return obj.comment

    comment_preview.short_description = "نظر"