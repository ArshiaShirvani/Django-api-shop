from django.contrib import admin
from django.utils.html import format_html

from .models import Cart, CartItem


# ============================================================
# Cart Item Inline
# ============================================================

class CartItemInline(admin.TabularInline):
    model = CartItem

    extra = 0
    show_change_link = True

    autocomplete_fields = [
        "variant",
    ]

    readonly_fields = [
        "product_preview",
        "variant_info",
        "price_display",
        "discount_display",
        "final_price_display",
        "subtotal_display",
        "stock_display",
        "availability_status",
        "created_date",
        "updated_date",
    ]

    fields = [
        "variant",
        "product_preview",
        "variant_info",
        "quantity",
        "stock_display",
        "price_display",
        "discount_display",
        "final_price_display",
        "subtotal_display",
        "availability_status",
        "created_date",
        "updated_date",
    ]

    ordering = [
        "-created_date",
    ]

    def product_preview(self, obj):
        if not obj or not obj.variant:
            return "-"

        image = obj.variant.product.main_image

        if not image:
            return "بدون تصویر"

        return format_html(
            '<img src="{}" width="60" height="60" '
            'style="object-fit:cover;border-radius:8px;" />',
            image.image.url,
        )

    product_preview.short_description = "تصویر"

    def variant_info(self, obj):
        if not obj or not obj.variant:
            return "-"

        variant = obj.variant

        return format_html(
            "<strong>{}</strong><br>"
            "سایز: {}<br>"
            "رنگ: {}<br>"
            "SKU: {}",
            variant.product.title,
            variant.size.title,
            variant.color.title,
            variant.sku,
        )

    variant_info.short_description = "اطلاعات محصول"

    def price_display(self, obj):
        if not obj or not obj.variant:
            return "-"

        price = f"{obj.variant.price:,}"

        return f"{price} تومان"

    price_display.short_description = "قیمت اصلی"

    def discount_display(self, obj):
        if not obj or not obj.variant:
            return "-"

        discount = obj.variant.discount_percent

        if discount > 0:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                '{}٪'
                "</span>",
                discount,
            )

        return "بدون تخفیف"

    discount_display.short_description = "تخفیف"

    def final_price_display(self, obj):
        if not obj or not obj.variant:
            return "-"

        price = f"{obj.variant.final_price:,}"

        return format_html(
            "<strong>{} تومان</strong>",
            price,
        )

    final_price_display.short_description = "قیمت نهایی"

    def subtotal_display(self, obj):
        if not obj or not obj.variant:
            return "-"

        subtotal = obj.variant.final_price * obj.quantity
        subtotal = f"{subtotal:,}"

        return format_html(
            "<strong>{} تومان</strong>",
            subtotal,
        )

    subtotal_display.short_description = "جمع آیتم"

    def stock_display(self, obj):
        if not obj or not obj.variant:
            return "-"

        stock = obj.variant.stock

        if stock <= 0:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                "تمام شده"
                "</span>"
            )

        if obj.quantity > stock:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                '{} عدد | ناکافی'
                "</span>",
                stock,
            )

        return format_html(
            '<span style="color:#2e7d32;font-weight:bold;">'
            '{} عدد'
            "</span>",
            stock,
        )

    stock_display.short_description = "موجودی"

    def availability_status(self, obj):
        if not obj or not obj.variant:
            return "-"

        variant = obj.variant

        if not variant.is_active:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                "غیرفعال"
                "</span>"
            )

        if variant.stock <= 0:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                "ناموجود"
                "</span>"
            )

        if obj.quantity > variant.stock:
            return format_html(
                '<span style="color:#f57c00;font-weight:bold;">'
                "موجودی ناکافی"
                "</span>"
            )

        return format_html(
            '<span style="color:#2e7d32;font-weight:bold;">'
            "قابل خرید"
            "</span>"
        )

    availability_status.short_description = "وضعیت"

    def has_add_permission(self, request, obj=None):
        return False


# ============================================================
# Cart Admin
# ============================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user_display",
        "phone_display",
        "items_count_display",
        "total_quantity_display",
        "total_price_display",
        "cart_status",
        "created_date",
        "updated_date",
    ]

    list_display_links = [
        "id",
        "user_display",
    ]

    search_fields = [
        "user__phone_number",
        "user__email",
    ]

    list_filter = [
        "created_date",
        "updated_date",
    ]

    readonly_fields = [
        "id",
        "user",
        "cart_summary",
        "created_date",
        "updated_date",
    ]

    fields = [
        "id",
        "user",
        "cart_summary",
        "created_date",
        "updated_date",
    ]

    inlines = [
        CartItemInline,
    ]

    ordering = [
        "-updated_date",
    ]

    list_per_page = 25

    date_hierarchy = "created_date"

    autocomplete_fields = [
        "user",
    ]

    actions = [
        "clear_selected_carts",
    ]

    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    def user_display(self, obj):
        return obj.user.phone_number

    user_display.short_description = "کاربر"

    # --------------------------------------------------------
    # Phone
    # --------------------------------------------------------

    def phone_display(self, obj):
        return obj.user.phone_number

    phone_display.short_description = "شماره تماس"

    # --------------------------------------------------------
    # Items Count
    # --------------------------------------------------------

    def items_count_display(self, obj):
        return obj.items.count()

    items_count_display.short_description = "تعداد آیتم"

    # --------------------------------------------------------
    # Total Quantity
    # --------------------------------------------------------

    def total_quantity_display(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

    total_quantity_display.short_description = "تعداد کالا"

    # --------------------------------------------------------
    # Total Price
    # --------------------------------------------------------

    def total_price_display(self, obj):
        total = sum(
            item.variant.final_price * item.quantity
            for item in obj.items.select_related(
                "variant"
            ).all()
        )

        total = f"{total:,}"

        return format_html(
            "<strong>{} تومان</strong>",
            total,
        )

    total_price_display.short_description = "مبلغ کل"

    # --------------------------------------------------------
    # Cart Status
    # --------------------------------------------------------

    def cart_status(self, obj):
        items = obj.items.select_related(
            "variant"
        ).all()

        if not items:
            return format_html(
                '<span style="color:#757575;">'
                "خالی"
                "</span>"
            )

        for item in items:
            variant = item.variant

            if not variant.is_active:
                return format_html(
                    '<span style="color:#d32f2f;font-weight:bold;">'
                    "نیازمند بررسی"
                    "</span>"
                )

            if variant.stock <= 0:
                return format_html(
                    '<span style="color:#d32f2f;font-weight:bold;">'
                    "نیازمند بررسی"
                    "</span>"
                )

            if item.quantity > variant.stock:
                return format_html(
                    '<span style="color:#f57c00;font-weight:bold;">'
                    "موجودی ناکافی"
                    "</span>"
                )

        return format_html(
            '<span style="color:#2e7d32;font-weight:bold;">'
            "آماده خرید"
            "</span>"
        )

    cart_status.short_description = "وضعیت"

    # --------------------------------------------------------
    # Cart Summary
    # --------------------------------------------------------

    def cart_summary(self, obj):
        if not obj:
            return "-"

        items = list(
            obj.items.select_related(
                "variant__product"
            ).all()
        )

        total_quantity = sum(
            item.quantity
            for item in items
        )

        total_price = sum(
            item.variant.final_price * item.quantity
            for item in items
        )

        unavailable_count = sum(
            1
            for item in items
            if (
                not item.variant.is_active
                or item.variant.stock <= 0
                or item.quantity > item.variant.stock
            )
        )

        total_price = f"{total_price:,}"

        return format_html(
            """
            <div style="
                display:flex;
                gap:12px;
                flex-wrap:wrap;
                margin:10px 0;
            ">

                <div style="
                    padding:12px 18px;
                    border:1px solid #ddd;
                    border-radius:8px;
                    min-width:120px;
                ">
                    <strong>آیتم‌ها</strong>
                    <br>
                    {}
                </div>

                <div style="
                    padding:12px 18px;
                    border:1px solid #ddd;
                    border-radius:8px;
                    min-width:120px;
                ">
                    <strong>تعداد کالا</strong>
                    <br>
                    {}
                </div>

                <div style="
                    padding:12px 18px;
                    border:1px solid #ddd;
                    border-radius:8px;
                    min-width:160px;
                ">
                    <strong>مبلغ کل</strong>
                    <br>
                    {} تومان
                </div>

                <div style="
                    padding:12px 18px;
                    border:1px solid #ddd;
                    border-radius:8px;
                    min-width:150px;
                ">
                    <strong>موارد مشکل‌دار</strong>
                    <br>
                    {}
                </div>

            </div>
            """,
            len(items),
            total_quantity,
            total_price,
            unavailable_count,
        )

    cart_summary.short_description = "خلاصه سبد خرید"

    # --------------------------------------------------------
    # Clear Selected Carts
    # --------------------------------------------------------

    @admin.action(
        description="خالی کردن سبدهای انتخاب‌شده"
    )
    def clear_selected_carts(
        self,
        request,
        queryset,
    ):
        total_items = 0

        for cart in queryset:
            count, _ = cart.items.all().delete()
            total_items += count

        self.message_user(
            request,
            f"{total_items} آیتم از سبدهای انتخاب‌شده حذف شد.",
        )

    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


# ============================================================
# Cart Item Admin
# ============================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "product_display",
        "variant_display",
        "user_display",
        "quantity",
        "stock_display",
        "price_display",
        "discount_display",
        "final_price_display",
        "subtotal_display",
        "availability_status",
        "created_date",
        "updated_date",
    ]

    list_display_links = [
        "id",
        "product_display",
    ]

    search_fields = [
        "cart__user__phone_number",
        "cart__user__email",
        "variant__product__title",
        "variant__sku",
    ]

    list_filter = [
        "variant__is_active",
        "variant__product",
        "variant__color",
        "variant__size",
        "created_date",
        "updated_date",
    ]

    autocomplete_fields = [
        "cart",
        "variant",
    ]

    readonly_fields = [
        "id",
        "cart",
        "variant",
        "product_preview",
        "price_display",
        "discount_display",
        "final_price_display",
        "subtotal_display",
        "stock_display",
        "availability_status",
        "created_date",
        "updated_date",
    ]

    fields = [
        "id",
        "cart",
        "variant",
        "product_preview",
        "quantity",
        "stock_display",
        "price_display",
        "discount_display",
        "final_price_display",
        "subtotal_display",
        "availability_status",
        "created_date",
        "updated_date",
    ]

    ordering = [
        "-updated_date",
    ]

    list_per_page = 50

    date_hierarchy = "created_date"

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    def product_display(self, obj):
        return obj.variant.product.title

    product_display.short_description = "محصول"

    # --------------------------------------------------------
    # Variant
    # --------------------------------------------------------

    def variant_display(self, obj):
        variant = obj.variant

        return format_html(
            "{} / {} / {}",
            variant.size.title,
            variant.color.title,
            variant.sku,
        )

    variant_display.short_description = "تنوع"

    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    def user_display(self, obj):
        return obj.cart.user.phone_number

    user_display.short_description = "کاربر"

    # --------------------------------------------------------
    # Original Price
    # --------------------------------------------------------

    def price_display(self, obj):
        price = f"{obj.variant.price:,}"

        return f"{price} تومان"

    price_display.short_description = "قیمت اصلی"

    # --------------------------------------------------------
    # Discount
    # --------------------------------------------------------

    def discount_display(self, obj):
        discount = obj.variant.discount_percent

        if discount:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                '{}٪'
                "</span>",
                discount,
            )

        return "بدون تخفیف"

    discount_display.short_description = "تخفیف"

    # --------------------------------------------------------
    # Final Price
    # --------------------------------------------------------

    def final_price_display(self, obj):
        price = f"{obj.variant.final_price:,}"

        return format_html(
            "<strong>{} تومان</strong>",
            price,
        )

    final_price_display.short_description = "قیمت نهایی"

    # --------------------------------------------------------
    # Subtotal
    # --------------------------------------------------------

    def subtotal_display(self, obj):
        subtotal = (
            obj.variant.final_price
            * obj.quantity
        )

        subtotal = f"{subtotal:,}"

        return format_html(
            "<strong>{} تومان</strong>",
            subtotal,
        )

    subtotal_display.short_description = "جمع"

    # --------------------------------------------------------
    # Stock
    # --------------------------------------------------------

    def stock_display(self, obj):
        stock = obj.variant.stock

        if stock <= 0:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                "ناموجود"
                "</span>"
            )

        if obj.quantity > stock:
            return format_html(
                '<span style="color:#f57c00;font-weight:bold;">'
                '{} عدد | ناکافی'
                "</span>",
                stock,
            )

        return format_html(
            '<span style="color:#2e7d32;font-weight:bold;">'
            '{} عدد'
            "</span>",
            stock,
        )

    stock_display.short_description = "موجودی"

    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    def availability_status(self, obj):
        variant = obj.variant

        if not variant.is_active:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                "غیرفعال"
                "</span>"
            )

        if variant.stock <= 0:
            return format_html(
                '<span style="color:#d32f2f;font-weight:bold;">'
                "ناموجود"
                "</span>"
            )

        if obj.quantity > variant.stock:
            return format_html(
                '<span style="color:#f57c00;font-weight:bold;">'
                "موجودی ناکافی"
                "</span>"
            )

        return format_html(
            '<span style="color:#2e7d32;font-weight:bold;">'
            "قابل خرید"
            "</span>"
        )

    availability_status.short_description = "وضعیت"

    # --------------------------------------------------------
    # Product Image
    # --------------------------------------------------------

    def product_preview(self, obj):
        if not obj or not obj.variant:
            return "-"

        image = obj.variant.product.main_image

        if not image:
            return "بدون تصویر"

        return format_html(
            '<img src="{}" width="100" height="100" '
            'style="object-fit:cover;border-radius:10px;" />',
            image.image.url,
        )

    product_preview.short_description = "تصویر محصول"

    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    def has_add_permission(self, request):
        return False