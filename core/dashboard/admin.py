from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "product",
        "created_date",
    )

    list_filter = (
        "created_date",
    )

    search_fields = (
        "user__phone_number",
        "product__title",
        "product__slug",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    readonly_fields = (
        "created_date",
    )

    ordering = (
        "-created_date",
    )

    list_per_page = 25