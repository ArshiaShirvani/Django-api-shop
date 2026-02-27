from rest_framework import serializers
from .models import (
    Product,
    ProductCategory,
    ProductSize,
    ProductColor,
    ProductVariant,
    ProductImages,
)



# CATEGORY 
class ProductCategorySerilizer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductCategory
        fields = ["id", "title", "slug", "parent", "children"]

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True)
        return ProductCategorySerilizer(qs, many=True).data



# SIZE
class ProductSizeSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ["id", "title"]



# COLOR
class ProductColorSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ["id", "title", "code"]



# PRODUCT LIST 
class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    category = ProductCategorySerilizer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "price",
            "original_price",
            "discount_percent",
            "main_image",
            "created_date",
        ]

    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first()
        return image.image.url if image else None

    def _get_active_variant(self, obj):
        return obj.variants.filter(is_active=True, stock__gt=0).first()

    def get_price(self, obj):
        variant = self._get_active_variant(obj)
        return variant.final_price if variant else None

    def get_original_price(self, obj):
        variant = self._get_active_variant(obj)
        return variant.price if variant else None

    def get_discount_percent(self, obj):
        variant = self._get_active_variant(obj)
        return variant.discount_percent if variant else None



# PRODUCT IMAGE
class ProductImageSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["id", "image", "is_main", "created_date"]



# VARIANT
class ProductVariantSerilizer(serializers.ModelSerializer):
    size = ProductSizeSerilizer(read_only=True)
    color = ProductColorSerilizer(read_only=True)
    final_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "size",
            "color",
            "price",
            "final_price",
            "discount_percent",
            "stock",
            "is_active",
            "sku",
            "created_date",
        ]


# PRODUCT DETAIL
class ProductDetailSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerilizer(many=True, read_only=True)
    images = ProductImageSerilizer(many=True, read_only=True)
    category = ProductCategorySerilizer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "category",
            "images",
            "variants",
            "created_date",
        ]