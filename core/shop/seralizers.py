from rest_framework import serializers

from .models import (
    Product,
    ProductCategory,
    ProductSize,
    ProductColor,
    ProductImages,
    ProductVariant,
    Feature,
    FeatureValue
)


# ===========================================
# CATEGORY
# ===========================================

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "title",
            "slug",
            "children",
        )

    def get_children(self, obj):
        return CategorySerializer(
            obj.children.all(),
            many=True,
            context=self.context
        ).data


class CategorySimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "title",
            "slug",
        )


# ===========================================
# SIZE
# ===========================================

class ProductSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductSize
        fields = (
            "id",
            "title",
        )


# ===========================================
# COLOR
# ===========================================

class ProductColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductColor
        fields = (
            "id",
            "title",
            "code",
        )


# ===========================================
# IMAGE
# ===========================================

class ProductImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = ProductImages
        fields = (
            "id",
            "image",
            "is_main",
        )


# ===========================================
# FEATURE VALUE
# ===========================================

class FeatureValueSerializer(serializers.ModelSerializer):

    feature = serializers.CharField(
        source="feature.title",
        read_only=True
    )

    class Meta:
        model = FeatureValue
        fields = (
            "feature",
            "value",
        )


# ===========================================
# VARIANT
# ===========================================

class ProductVariantSerializer(serializers.ModelSerializer):

    size = ProductSizeSerializer(
        read_only=True
    )

    color = ProductColorSerializer(
        read_only=True
    )

    final_price = serializers.IntegerField(
        read_only=True
    )

    has_discount = serializers.BooleanField(
        read_only=True
    )

    is_available = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = ProductVariant

        fields = (
            "id",

            "size",
            "color",

            "price",
            "final_price",

            "discount_percent",

            "stock",

            "is_available",

            "has_discount",

            "sku",
        )
        
# ===========================================
# PRODUCT LIST
# ===========================================

class ProductListSerializer(serializers.ModelSerializer):

    categories = CategorySimpleSerializer(
        many=True,
        read_only=True
    )

    price = serializers.IntegerField(
        source="best_variant_price",
        read_only=True
    )

    original_price = serializers.IntegerField(
        source="best_variant_original_price",
        read_only=True
    )

    discount_percent = serializers.IntegerField(
        source="best_variant_discount",
        read_only=True
    )

    main_image = serializers.SerializerMethodField()

    has_discount = serializers.SerializerMethodField()

    class Meta:

        model = Product

        fields = (

            "id",

            "title",

            "slug",

            "brief_description",

            "categories",

            "price",

            "original_price",

            "discount_percent",

            "has_discount",

            "main_image",

            "created_date",

        )

    def get_main_image(self, obj):

        image = obj.main_image

        if image:
            request = self.context.get("request")

            if request:
                return request.build_absolute_uri(
                    image.image.url
                )

            return image.image.url

        return None

    def get_has_discount(self, obj):

        return (
            obj.best_variant_discount is not None
            and
            obj.best_variant_discount > 0
        )


# ===========================================
# PRODUCT DETAIL
# ===========================================

class ProductDetailSerializer(serializers.ModelSerializer):

    categories = CategorySimpleSerializer(
        many=True,
        read_only=True
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    variants = ProductVariantSerializer(
        many=True,
        read_only=True
    )

    feature_values = FeatureValueSerializer(
        many=True,
        read_only=True
    )

    main_image = serializers.SerializerMethodField()

    min_price = serializers.ReadOnlyField()

    max_discount = serializers.ReadOnlyField()

    has_stock = serializers.ReadOnlyField()

    class Meta:

        model = Product

        fields = (

            "id",

            "title",

            "slug",

            "brief_description",

            "description",

            "categories",

            "main_image",

            "images",

            "variants",

            "feature_values",

            "min_price",

            "max_discount",

            "has_stock",

            "created_date",

        )

    def get_main_image(self, obj):

        image = obj.main_image

        if image:

            request = self.context.get("request")

            if request:

                return request.build_absolute_uri(
                    image.image.url
                )

            return image.image.url

        return None