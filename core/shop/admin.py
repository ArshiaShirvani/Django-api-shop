from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Product,
    ProductCategory,
    ProductSize,
    ProductColor,
    ProductVariant,
    ProductImages,
    Feature,
    FeatureValue
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "parent", "is_root", "created_date")
    list_filter = ("parent",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("parent", "title")


class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    readonly_fields = ("image_preview",)
    fields = ("image", "image_preview", "is_main")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" />', obj.image.url)
        return "-"
    image_preview.short_description = "پیش نمایش"



class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ("final_price",)
    fields = (
        "size",
        "color",
        "price",
        "discount_percent",
        "final_price",
        "stock",
        "is_active",
        "sku",
    )


class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 1



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "category_list",
        "created_date"
    )

    list_filter = ("status", "categories")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)

    inlines = [
        ProductImagesInline,
        ProductVariantInline,
        FeatureValueInline
    ]

    def category_list(self, obj):
        return ", ".join([c.title for c in obj.categories.all()])
    category_list.short_description = "دسته بندی ها"



@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "color_display",
        "price",
        "discount_percent",
        "final_price",
        "stock",
        "is_active"
    )

    list_filter = ("is_active", "color", "size")
    search_fields = ("product__title", "sku")
    readonly_fields = ("final_price",)

    def color_display(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;background:{};border-radius:4px;"></span> {}',
            obj.color.code,
            obj.color.title
        )
    color_display.short_description = "رنگ"



@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("title", "color_preview", "code")
    search_fields = ("title", "code")

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:30px;height:20px;background:{};"></span>',
            obj.code
        )
    color_preview.short_description = "نمایش رنگ"



@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    search_fields = ("title",)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    search_fields = ("title",)


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ("product", "image_preview", "is_main", "created_date")
    list_filter = ("is_main",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        return "-"
    image_preview.short_description = "پیش نمایش"



@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    list_display = ("product", "feature", "value")
    list_filter = ("feature",)
    search_fields = ("product__title", "value")