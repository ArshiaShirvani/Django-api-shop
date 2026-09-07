from django.contrib import admin

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    CouponUsage,
    Order,
    OrderItem,
)


# =========================================================
# ADDRESS
# =========================================================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "title",
        "recipient_name",
        "recipient_phone",
        "province",
        "city",
        "is_default",
        "created_date",
    )

    list_filter = (
        "is_default",
        "province",
        "city",
        "created_date",
    )

    search_fields = (
        "user__phone_number",
        "recipient_name",
        "recipient_phone",
        "province",
        "city",
        "address",
        "postal_code",
    )

    ordering = ("-created_date",)

    list_per_page = 25


# =========================================================
# SHIPPING METHOD
# =========================================================

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "code",
        "base_cost",
        "free_shipping_minimum",
        "is_active",
        "display_order",
        "created_date",
    )

    list_filter = (
        "is_active",
        "created_date",
    )

    search_fields = (
        "title",
        "code",
        "description",
    )

    list_editable = (
        "is_active",
        "display_order",
        "base_cost",
    )

    prepopulated_fields = {
        "code": ("title",),
    }

    ordering = (
        "display_order",
        "-created_date",
    )

    list_per_page = 25


# =========================================================
# COUPON
# =========================================================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "code",
        "discount_type",
        "discount_value",
        "minimum_order_amount",
        "usage_limit",
        "usage_limit_per_user",
        "is_global",
        "is_active",
        "start_date",
        "end_date",
    )

    list_filter = (
        "discount_type",
        "is_global",
        "is_active",
        "start_date",
        "end_date",
    )

    search_fields = (
        "code",
        "users__phone_number",
    )

    filter_horizontal = (
        "users",
    )

    ordering = (
        "-created_date",
    )

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "code",
                    "discount_type",
                    "discount_value",
                    "max_discount_amount",
                    "minimum_order_amount",
                )
            },
        ),
        (
            "زمان اعتبار",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "is_active",
                )
            },
        ),
        (
            "محدودیت استفاده",
            {
                "fields": (
                    "usage_limit",
                    "usage_limit_per_user",
                )
            },
        ),
        (
            "دسترسی کاربران",
            {
                "fields": (
                    "is_global",
                    "users",
                )
            },
        ),
    )


# =========================================================
# COUPON USAGE
# =========================================================

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "coupon",
        "user",
        "order",
        "used_date",
    )

    list_filter = (
        "used_date",
    )

    search_fields = (
        "coupon__code",
        "user__phone_number",
        "order__tracking_code",
    )

    readonly_fields = (
        "coupon",
        "user",
        "order",
        "used_date",
    )

    ordering = (
        "-used_date",
    )

    list_per_page = 25


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    fields = (
        "variant",
        "product_title",
        "size",
        "color",
        "sku",
        "unit_price",
        "quantity",
        "subtotal",
    )

    readonly_fields = (
        "product_title",
        "size",
        "color",
        "sku",
        "unit_price",
        "subtotal",
    )

    autocomplete_fields = (
        "variant",
    )


# =========================================================
# ORDER
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "tracking_code",
        "user",
        "status",
        "subtotal",
        "discount",
        "tax",
        "shipping_cost",
        "total",
        "created_date",
    )

    list_filter = (
        "status",
        "created_date",
        "shipping_method",
    )

    search_fields = (
        "tracking_code",
        "user__phone_number",
        "recipient_name",
        "recipient_phone",
        "postal_code",

    )

    readonly_fields = (
        "tracking_code",
        "created_date",
        "updated_date",
        "subtotal",
        "tax",
        "discount",
        "shipping_cost",
        "total",

    )

    autocomplete_fields = (
        "user",
        "coupon",
        "shipping_method",
    )

    inlines = (
        OrderItemInline,
    )

    ordering = (
        "-created_date",
    )

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "user",
                    "status",
                    "tracking_code",
                )
            },
        ),
        (
            "مبالغ",
            {
                "fields": (
                    "subtotal",
                    "discount",
                    "tax",
                    "shipping_cost",
                    "total",
                )
            },
        ),
        (
            "تخفیف",
            {
                "fields": (
                    "coupon",
                    
                )
            },
        ),
        (
            "ارسال",
            {
                "fields": (
                    "shipping_method",
                )
            },
        ),
        (
            "آدرس گیرنده",
            {
                "fields": (
                    "recipient_name",
                    "recipient_phone",
                    "province",
                    "city",
                    "address",
                    "postal_code",
                    "plaque",
                    "unit",
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