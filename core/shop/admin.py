from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Product,
    ProductCategory,
    ProductImages,
    ProductVariant,
    ProductSize,
    ProductColor,
    Feature,
    FeatureValue,
    SizeGuide,
)


# ======================================
# SIZE GUIDE INLINE
# ======================================
class SizeGuideInline(admin.TabularInline):

    model = SizeGuide

    extra = 1

    fields = [
        "feature",
        "value",
        "image",
    ]

    show_change_link = True

# ======================================
# IMAGE INLINE
# ======================================

class ProductImageInline(
    admin.TabularInline
):

    model = ProductImages

    extra = 1

    fields = (
        "image",
        "preview",
        "is_main",
    )

    readonly_fields = (
        "preview",
    )


    def preview(self, obj):

        if obj.image:

            return format_html(

                '<img src="{}" width="80" height="80" style="object-fit:cover;">',

                obj.image.url

            )

        return "-"

    preview.short_description = "پیش نمایش"


# ======================================
# VARIANT INLINE
# ======================================

class ProductVariantInline(
    admin.TabularInline
):

    model = ProductVariant

    extra = 1

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


    readonly_fields = (

        "final_price",

    )


    def final_price(self,obj):

        if obj:

            return f"{obj.final_price:,} تومان"

        return "-"

    final_price.short_description = "قیمت نهایی"



# ======================================
# FEATURE INLINE
# ======================================

class FeatureValueInline(
    admin.TabularInline
):

    model = FeatureValue

    extra = 1



# ======================================
# PRODUCT ADMIN
# ======================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):


    list_display = (

        "title",

        "status",

        "thumbnail",

        "created_date",

    )


    list_filter = (

        "status",

        "categories",

    )


    search_fields = (

        "title",

        "slug",

        "brief_description",

    )


    prepopulated_fields = {

        "slug":(
            "title",
        )

    }


    filter_horizontal = (

        "categories",

    )


    readonly_fields = (

        "thumbnail",

    )


    inlines = (

        ProductImageInline,

        ProductVariantInline,

        FeatureValueInline,
        
        SizeGuideInline,

    )



    def thumbnail(self,obj):

        image = obj.main_image


        if image:

            return format_html(

                '<img src="{}" width="60" height="60" style="object-fit:cover;">',

                image.image.url

            )

        return "-"



    thumbnail.short_description = "تصویر"



# ======================================
# CATEGORY ADMIN
# ======================================


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):


    list_display = (

        "title",

        "parent",

        "created_date",

    )


    search_fields = (

        "title",

        "slug",

    )


    prepopulated_fields = {

        "slug":(
            "title",
        )

    }



# ======================================
# VARIANT ADMIN
# ======================================


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):


    list_display = (

        "product",

        "size",

        "color",

        "price",

        "final_price",

        "stock",

        "is_active",

    )


    list_filter = (

        "is_active",

        "color",

        "size",

    )


    search_fields = (

        "product__title",

        "sku",

    )



# ======================================
# IMAGE ADMIN
# ======================================


@admin.register(ProductImages)
class ProductImageAdmin(admin.ModelAdmin):


    list_display = (

        "product",

        "preview",

        "is_main",

    )


    list_filter = (

        "is_main",

    )


    def preview(self,obj):

        if obj.image:

            return format_html(

                '<img src="{}" width="70">',

                obj.image.url

            )

        return "-"



# ======================================
# SIMPLE MODELS
# ======================================


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):

    search_fields = (
        "title",
    )



@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):

    list_display = (

        "title",

        "code",

    )



@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):

    search_fields = (

        "title",

    )
    
