from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    CouponUsage,
    Order,
    OrderItem,
)


# =========================================================
# Address
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

    list_display_links = (
        "id",
        "title",
    )

    list_filter = (
        "is_default",
        "province",
        "created_date",
    )

    search_fields = (
        "user__phone_number",
        "user__email",
        "title",
        "recipient_name",
        "recipient_phone",
        "province",
        "city",
        "postal_code",
        "address",
    )

    readonly_fields = (
        "created_date",
        "updated_date",
    )

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "اطلاعات گیرنده",
            {
                "fields": (
                    "title",
                    "recipient_name",
                    "recipient_phone",
                )
            },
        ),
        (
            "آدرس",
            {
                "fields": (
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
            "تنظیمات",
            {
                "fields": (
                    "is_default",
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


# =========================================================
# Shipping Method
# =========================================================

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "code",
        "base_cost_display",
        "free_shipping_display",
        "is_active",
        "display_order",
        "created_date",
    )

    list_display_links = (
        "id",
        "title",
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
    )

    readonly_fields = (
        "created_date",
        "updated_date",
    )

    ordering = (
        "display_order",
        "id",
    )

    list_per_page = 25

    @admin.display(description="هزینه پایه")
    def base_cost_display(self, obj):
        return f"{obj.base_cost:,} تومان"

    @admin.display(description="حداقل ارسال رایگان")
    def free_shipping_display(self, obj):

        if obj.free_shipping_minimum is None:
            return "فعال نیست"

        return f"{obj.free_shipping_minimum:,} تومان"

    fieldsets = (
        (
            "اطلاعات روش ارسال",
            {
                "fields": (
                    "title",
                    "code",
                    "description",
                )
            },
        ),
        (
            "هزینه",
            {
                "fields": (
                    "base_cost",
                    "free_shipping_minimum",
                )
            },
        ),
        (
            "تنظیمات",
            {
                "fields": (
                    "is_active",
                    "display_order",
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


# =========================================================
# Coupon
# =========================================================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "code",
        "discount_display",
        "minimum_order_display",
        "start_date",
        "end_date",
        "usage_limit",
        "usage_limit_per_user",
        "is_active",
        "public_display",
    )

    list_display_links = (
        "id",
        "code",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "start_date",
        "end_date",
        "created_date",
    )

    search_fields = (
        "code",
        "allowed_users__phone_number",
        "allowed_users__email",
    )

    filter_horizontal = (
        "allowed_users",
    )

    readonly_fields = (
        "created_date",
        "updated_date",
        "is_valid_time_display",
        "is_public_display",
    )

    list_per_page = 25

    @admin.display(description="تخفیف")
    def discount_display(self, obj):

        if obj.discount_type == Coupon.DiscountType.PERCENTAGE:

            value = f"{obj.discount_value}%"

            if obj.max_discount_amount:
                value += (
                    f" | سقف "
                    f"{obj.max_discount_amount:,} تومان"
                )

            return value

        return f"{obj.discount_value:,} تومان"

    @admin.display(description="حداقل سفارش")
    def minimum_order_display(self, obj):
        return f"{obj.minimum_order_amount:,} تومان"

    @admin.display(boolean=True, description="عمومی")
    def public_display(self, obj):
        return obj.is_public

    @admin.display(description="وضعیت زمانی")
    def is_valid_time_display(self, obj):

        if obj.is_valid_time:
            return format_html(
                '<span style="color:green;font-weight:bold;">فعال</span>'
            )

        return format_html(
            '<span style="color:red;font-weight:bold;">غیرفعال</span>'
        )

    @admin.display(boolean=True, description="کد عمومی")
    def is_public_display(self, obj):
        return obj.is_public

    fieldsets = (
        (
            "اطلاعات کد تخفیف",
            {
                "fields": (
                    "code",
                    "discount_type",
                    "discount_value",
                    "max_discount_amount",
                )
            },
        ),
        (
            "شرایط استفاده",
            {
                "fields": (
                    "minimum_order_amount",
                    "usage_limit",
                    "usage_limit_per_user",
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
                    "is_valid_time_display",
                )
            },
        ),
        (
            "کاربران مجاز",
            {
                "fields": (
                    "allowed_users",
                    "is_public_display",
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


# =========================================================
# Coupon Usage
# =========================================================

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "coupon",
        "user",
        "order",
        "discount_display",
        "created_date",
    )

    list_display_links = (
        "id",
        "coupon",
    )

    list_filter = (
        "coupon",
        "created_date",
    )

    search_fields = (
        "coupon__code",
        "user__phone_number",
        "user__email",
        "order__order_number",
    )

    readonly_fields = (
        "coupon",
        "user",
        "order",
        "discount_amount",
        "created_date",
    )

    list_per_page = 25

    @admin.display(description="مبلغ تخفیف")
    def discount_display(self, obj):
        return f"{obj.discount_amount:,} تومان"


# =========================================================
# Order Item Inline
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    can_delete = False

    readonly_fields = (
        "variant",
        "product_title",
        "sku",
        "size",
        "color",
        "color_code",
        "original_unit_price",
        "discount_percent",
        "unit_price",
        "quantity",
        "subtotal",
        "created_date",
        "updated_date",
    )

    fields = (
        "variant",
        "product_title",
        "sku",
        "size",
        "color",
        "color_code",
        "original_unit_price",
        "discount_percent",
        "unit_price",
        "quantity",
        "subtotal",
        "created_date",
    )

    ordering = (
        "id",
    )

    show_change_link = True


# =========================================================
# Order
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order_number",
        "user",
        "status_badge",
        "subtotal_display",
        "discount_display",
        "shipping_cost_display",
        "total_price_display",
        "coupon_code",
        "shipping_title",
        "created_date",
    )

    list_display_links = (
        "id",
        "order_number",
    )

    list_filter = (
        "status",
        "shipping_method",
        "coupon",
        "created_date",
        "paid_at",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
    )

    search_fields = (
        "order_number",
        "user__phone_number",
        "user__email",
        "coupon_code",
        "tracking_code",
        "recipient_name",
        "recipient_phone",
        "postal_code",
    )

    readonly_fields = (
        "order_number",
        "user",
        "coupon",
        "coupon_code",
        "coupon_discount",
        "shipping_method",
        "shipping_title",
        "shipping_cost",
        "recipient_name",
        "recipient_phone",
        "province",
        "city",
        "address",
        "postal_code",
        "plaque",
        "unit",
        "subtotal",
        "discount_amount",
        "total_price",
        "created_date",
        "updated_date",
        "paid_at",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
        "is_paid_display",
        "is_cancelled_display",
    )

    list_per_page = 25

    date_hierarchy = "created_date"

    inlines = (
        OrderItemInline,
    )

    ordering = (
        "-created_date",
    )

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "is_paid_display",
                    "is_cancelled_display",
                )
            },
        ),
        (
            "کد تخفیف",
            {
                "fields": (
                    "coupon",
                    "coupon_code",
                    "coupon_discount",
                )
            },
        ),
        (
            "روش ارسال",
            {
                "fields": (
                    "shipping_method",
                    "shipping_title",
                    "shipping_cost",
                    "tracking_code",
                )
            },
        ),
        (
            "اطلاعات گیرنده",
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
            "مبالغ سفارش",
            {
                "fields": (
                    "subtotal",
                    "discount_amount",
                    "total_price",
                )
            },
        ),
        (
            "تاریخ‌ها",
            {
                "fields": (
                    "paid_at",
                    "shipped_at",
                    "delivered_at",
                    "cancelled_at",
                    "created_date",
                    "updated_date",
                )
            },
        ),
    )

    @admin.display(description="وضعیت")
    def status_badge(self, obj):

        status_text = obj.get_status_display()

        if obj.status == Order.Status.PENDING:
            color = "#f59e0b"

        elif obj.status == Order.Status.PAID:
            color = "#10b981"

        elif obj.status == Order.Status.PROCESSING:
            color = "#3b82f6"

        elif obj.status == Order.Status.READY_TO_SHIP:
            color = "#6366f1"

        elif obj.status == Order.Status.SHIPPED:
            color = "#8b5cf6"

        elif obj.status == Order.Status.DELIVERED:
            color = "#059669"

        elif obj.status == Order.Status.CANCELLED:
            color = "#ef4444"

        else:
            color = "#6b7280"

        return format_html(
            '<span style="'
            'background:{};'
            'color:white;'
            'padding:4px 9px;'
            'border-radius:6px;'
            'font-weight:bold;'
            '">'
            '{}'
            '</span>',
            color,
            status_text,
        )

    @admin.display(description="مبلغ کالاها")
    def subtotal_display(self, obj):
        return f"{obj.subtotal:,} تومان"

    @admin.display(description="تخفیف")
    def discount_display(self, obj):
        return f"{obj.discount_amount:,} تومان"

    @admin.display(description="هزینه ارسال")
    def shipping_cost_display(self, obj):
        return f"{obj.shipping_cost:,} تومان"

    @admin.display(description="مبلغ نهایی")
    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    @admin.display(boolean=True, description="پرداخت شده")
    def is_paid_display(self, obj):
        return obj.is_paid

    @admin.display(boolean=True, description="لغو شده")
    def is_cancelled_display(self, obj):
        return obj.is_cancelled


# =========================================================
# Order Item
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product_title",
        "sku",
        "size",
        "color",
        "original_unit_price_display",
        "unit_price_display",
        "quantity",
        "subtotal_display",
        "created_date",
    )

    list_display_links = (
        "id",
        "product_title",
    )

    list_filter = (
        "discount_percent",
        "created_date",
    )

    search_fields = (
        "order__order_number",
        "product_title",
        "sku",
        "size",
        "color",
    )

    readonly_fields = (
        "order",
        "variant",
        "product_title",
        "sku",
        "size",
        "color",
        "color_code",
        "original_unit_price",
        "discount_percent",
        "unit_price",
        "quantity",
        "subtotal",
        "created_date",
        "updated_date",
    )

    list_per_page = 25

    ordering = (
        "-created_date",
    )

    fieldsets = (
        (
            "سفارش",
            {
                "fields": (
                    "order",
                    "variant",
                )
            },
        ),
        (
            "اطلاعات محصول",
            {
                "fields": (
                    "product_title",
                    "sku",
                    "size",
                    "color",
                    "color_code",
                )
            },
        ),
        (
            "قیمت",
            {
                "fields": (
                    "original_unit_price",
                    "discount_percent",
                    "unit_price",
                    "quantity",
                    "subtotal",
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

    @admin.display(description="قیمت اصلی")
    def original_unit_price_display(self, obj):
        return f"{obj.original_unit_price:,} تومان"

    @admin.display(description="قیمت نهایی واحد")
    def unit_price_display(self, obj):
        return f"{obj.unit_price:,} تومان"

    @admin.display(description="جمع")
    def subtotal_display(self, obj):
        return f"{obj.subtotal:,} تومان"