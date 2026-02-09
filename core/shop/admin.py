from django.contrib import admin
from .models import (
    ProductCategory,
    Product,
    ProductSize,
    ProductColor,
    ProductImages,
    ProductVariant
)



class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ('image', 'is_main', 'created_date', 'updated_date')
    readonly_fields = ('created_date', 'updated_date')
    show_change_link = True
    
    def has_delete_permission(self, request, obj=None):
        if obj:
            main_images = obj.images.filter(is_main=True)
            if main_images.count() <= 1:
                return False  
        return super().has_delete_permission(request, obj)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'price', 'discount_percent', 'stock', 'is_active', 'sku', 'created_date', 'updated_date')
    readonly_fields = ('created_date', 'updated_date')
    show_change_link = True

    def save_new(self, form, commit=True):
        
        instance = form.save(commit=False)
        if ProductVariant.objects.filter(product=instance.product, size=instance.size, color=instance.color).exists():
            raise ValueError("این ترکیب محصول، سایز و رنگ قبلاً ثبت شده است.")
        if commit:
            instance.save()
        return instance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date', 'updated_date')
    list_filter = ('status', 'categories')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImagesInline, ProductVariantInline]
    filter_horizontal = ('categories',)
    readonly_fields = ('created_date', 'updated_date')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_date', 'updated_date')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    readonly_fields = ('created_date', 'updated_date')


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date', 'updated_date')
    search_fields = ('title',)
    readonly_fields = ('created_date', 'updated_date')


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'created_date', 'updated_date')
    search_fields = ('title', 'code')
    readonly_fields = ('created_date', 'updated_date')


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_main', 'created_date', 'updated_date')
    list_filter = ('product', 'is_main')
    readonly_fields = ('created_date', 'updated_date')
    search_fields = ('product__title',)
