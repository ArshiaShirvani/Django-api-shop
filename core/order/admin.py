from django.contrib import admin
from .models import (
    OrderModel,
    OrderItemsModel,
    CouponModel,
    UserAddressModel
)


class OrderItemsInline(admin.TabularInline):
    model = OrderItemsModel
    extra = 0
    readonly_fields = ["variant", "quantity", "price", "created_date", "updated_date"]
    can_delete = False
    show_change_link = True



@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "total_price",
        "coupon",
        "tax_percent",
        "get_shipping_method_display",
        "get_status_display",
        "created_date",
        "updated_date",
    ]
    list_filter = ["status", "shipping_method", "created_date", "updated_date"]
    search_fields = ["user__phone_number", "user__full_name", "coupon__code", "id"]
    readonly_fields = ["created_date", "updated_date"]
    inlines = [OrderItemsInline]



@admin.register(UserAddressModel)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "email",
        "state",
        "city",
        "zip_code",
        "plate",
        "created_date",
        "updated_date",
    ]
    search_fields = ["user__phone_number", "user__full_name", "address"]
    readonly_fields = ["created_date", "updated_date"]



@admin.register(CouponModel)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "code",
        "discount_percent",
        "is_active",
        "expiration_date",
        "created_date",
        "updated_date",
    ]
    list_filter = ["is_active", "expiration_date", "created_date"]
    search_fields = ["code", "allowed_users__phone_number", "used_by__phone_number"]
    filter_horizontal = ["allowed_users", "used_by"]
    readonly_fields = ["created_date", "updated_date"]
