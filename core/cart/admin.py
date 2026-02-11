from django.contrib import admin
from .models import Cart, CartItem


# =====================================
# CartItem Inline داخل Cart
# =====================================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    
    readonly_fields = [
        "price",
        "subtotal",
        "created_date",
        "updated_date",
    ]
    fields = [
        "variant",
        "quantity",
        "price",
        "subtotal",
        "created_date",
    ]
    show_change_link = True


# =====================================
# Cart (سبد هر کاربر)
# =====================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "items_count",
        "cart_total_price",
        "created_date",
        "updated_date",
    ]

    search_fields = [
        "user__phone_number",
    ]

    list_filter = [
        "created_date",
        "updated_date",
    ]

    readonly_fields = [
        "created_date",
        "updated_date",
        "cart_total_price",
    ]

    inlines = [CartItemInline]

    # --- computed fields ---
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "تعداد آیتم‌ها"

    def cart_total_price(self, obj):
        return sum(item.subtotal for item in obj.items.all())
    cart_total_price.short_description = "مجموع قیمت سبد"


# =====================================
# CartItem (مدیریت مستقل آیتم‌ها)
# =====================================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cart",
        "product_title",
        "variant",
        "quantity",
        "price",
        "subtotal",
        "created_date",
    ]

    list_select_related = [
        "cart",
        "variant",
        "variant__product",
        "variant__size",
        "variant__color",
    ]

    search_fields = [
        "cart__user__phone_number",
        "variant__product__title",
        "variant__sku",
    ]

    list_filter = [
        "created_date",
        "variant__product",
        "variant__size",
        "variant__color",
    ]

    readonly_fields = [
        "price",
        "subtotal",
        "created_date",
        "updated_date",
    ]

    raw_id_fields = ["variant"]

    # --- helpers ---
    def product_title(self, obj):
        return obj.variant.product.title
    product_title.short_description = "محصول"
