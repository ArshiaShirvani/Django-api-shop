from rest_framework import serializers

from shop.models import (
    Product,
    ProductStatus,
    ProductCategory,
    ProductImages,
    ProductVariant,
    ProductSize,
    ProductColor,
    Feature,
    FeatureValue,
    SizeGuide,
)


# ==========================================================
# CATEGORY
# ==========================================================

class AdminProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "title",
            "slug",
            "parent",
        )


# ==========================================================
# IMAGE
# ==========================================================

class AdminProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImages
        fields = (
            "id",
            "image",
            "is_main",
            "created_date",
        )

        read_only_fields = (
            "id",
            "created_date",
        )


# ==========================================================
# VARIANT
# ==========================================================

class AdminProductVariantSerializer(serializers.ModelSerializer):

    size = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

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
            "discount_percent",
            "final_price",
            "stock",
            "is_active",
            "is_available",
            "has_discount",
            "sku",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "final_price",
            "has_discount",
            "is_available",
            "created_date",
            "updated_date",
        )

    def get_size(self, obj):

        return {
            "id": obj.size.id,
            "title": obj.size.title,
        }

    def get_color(self, obj):

        return {
            "id": obj.color.id,
            "title": obj.color.title,
            "code": obj.color.code,
        }


# ==========================================================
# FEATURE VALUE
# ==========================================================

class AdminProductFeatureSerializer(serializers.ModelSerializer):

    feature = serializers.SerializerMethodField()

    class Meta:
        model = FeatureValue

        fields = (
            "id",
            "feature",
            "value",
        )

    def get_feature(self, obj):

        return {
            "id": obj.feature.id,
            "title": obj.feature.title,
        }


# ==========================================================
# SIZE GUIDE
# ==========================================================

class AdminProductSizeGuideSerializer(serializers.ModelSerializer):

    class Meta:
        model = SizeGuide

        fields = (
            "id",
            "feature",
            "value",
            "image",
        )


# ==========================================================
# PRODUCT LIST
# ==========================================================

class AdminProductListSerializer(serializers.ModelSerializer):

    categories = serializers.SerializerMethodField()

    main_image = serializers.SerializerMethodField()

    min_price = serializers.IntegerField(
        read_only=True
    )

    max_discount = serializers.IntegerField(
        read_only=True
    )

    has_stock = serializers.BooleanField(
        read_only=True
    )

    variants_count = serializers.IntegerField(
        read_only=True
    )

    total_stock = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Product

        fields = (
            "id",
            "title",
            "slug",
            "brief_description",
            "categories",
            "status",
            "main_image",
            "min_price",
            "max_discount",
            "has_stock",
            "variants_count",
            "total_stock",
            "created_date",
            "updated_date",
        )

    def get_categories(self, obj):

        return [
            {
                "id": category.id,
                "title": category.title,
                "slug": category.slug,
            }
            for category in obj.categories.all()
        ]

    def get_main_image(self, obj):

        image = obj.main_image

        if not image:
            return None

        request = self.context.get("request")

        image_url = image.image.url

        if request:
            return request.build_absolute_uri(image_url)

        return image_url


# ==========================================================
# PRODUCT DETAIL
# ==========================================================

class AdminProductDetailSerializer(serializers.ModelSerializer):

    categories = serializers.SerializerMethodField()

    images = AdminProductImageSerializer(
        many=True,
        read_only=True,
    )

    variants = AdminProductVariantSerializer(
        many=True,
        read_only=True,
    )

    feature_values = AdminProductFeatureSerializer(
        many=True,
        read_only=True,
    )

    size_guides = AdminProductSizeGuideSerializer(
        many=True,
        read_only=True,
    )

    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = (
            "id",
            "title",
            "slug",
            "brief_description",
            "description",
            "categories",
            "status",
            "main_image",
            "images",
            "variants",
            "feature_values",
            "size_guides",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "main_image",
            "images",
            "variants",
            "feature_values",
            "size_guides",
            "created_date",
            "updated_date",
        )

    def get_categories(self, obj):

        return [
            {
                "id": category.id,
                "title": category.title,
                "slug": category.slug,
            }
            for category in obj.categories.all()
        ]

    def get_main_image(self, obj):

        image = obj.main_image

        if not image:
            return None

        request = self.context.get("request")

        image_url = image.image.url

        if request:
            return request.build_absolute_uri(image_url)

        return image_url


# ==========================================================
# VARIANT INPUT
# ==========================================================

class AdminProductVariantInputSerializer(serializers.Serializer):

    id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    size = serializers.PrimaryKeyRelatedField(
        queryset=ProductSize.objects.all()
    )

    color = serializers.PrimaryKeyRelatedField(
        queryset=ProductColor.objects.all()
    )

    price = serializers.IntegerField(
        min_value=0
    )

    discount_percent = serializers.IntegerField(
        min_value=0,
        max_value=100,
        default=0,
    )

    stock = serializers.IntegerField(
        min_value=0,
        default=0,
    )

    is_active = serializers.BooleanField(
        default=True
    )

    sku = serializers.CharField(
        max_length=50
    )


# ==========================================================
# FEATURE INPUT
# ==========================================================

class AdminProductFeatureInputSerializer(serializers.Serializer):

    id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    feature = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all()
    )

    value = serializers.CharField(
        max_length=255
    )


# ==========================================================
# SIZE GUIDE INPUT
# ==========================================================

class AdminProductSizeGuideInputSerializer(serializers.Serializer):

    id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    feature = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    value = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    image = serializers.ImageField(
        required=False,
        allow_null=True,
    )


# ==========================================================
# PRODUCT CREATE
# ==========================================================

class AdminProductCreateSerializer(serializers.ModelSerializer):

    categories = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        many=True,
        required=False,
    )

    variants = AdminProductVariantInputSerializer(
        many=True,
        required=False,
    )

    feature_values = AdminProductFeatureInputSerializer(
        many=True,
        required=False,
    )

    size_guides = AdminProductSizeGuideInputSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Product

        fields = (
            "title",
            "slug",
            "brief_description",
            "description",
            "categories",
            "status",
            "variants",
            "feature_values",
            "size_guides",
        )

    def validate_title(self, value):

        if Product.objects.filter(
            title=value
        ).exists():

            raise serializers.ValidationError(
                "محصولی با این عنوان قبلاً وجود دارد."
            )

        return value

    def validate_slug(self, value):

        if Product.objects.filter(
            slug=value
        ).exists():

            raise serializers.ValidationError(
                "محصولی با این اسلاگ قبلاً وجود دارد."
            )

        return value

    def validate(self, attrs):

        # ------------------------------------------
        # VARIANTS
        # ------------------------------------------

        variants = attrs.get(
            "variants",
            []
        )

        combinations = set()
        skus = set()

        for variant in variants:

            combination = (
                variant["size"].id,
                variant["color"].id,
            )

            if combination in combinations:

                raise serializers.ValidationError({
                    "variants": (
                        "ترکیب سایز و رنگ تکراری است."
                    )
                })

            combinations.add(
                combination
            )

            sku = variant["sku"]

            if sku in skus:

                raise serializers.ValidationError({
                    "variants": (
                        f"کد SKU تکراری است: {sku}"
                    )
                })

            if ProductVariant.objects.filter(
                sku=sku
            ).exists():

                raise serializers.ValidationError({
                    "variants": (
                        f"کد SKU قبلاً استفاده شده است: {sku}"
                    )
                })

            skus.add(sku)

        # ------------------------------------------
        # FEATURES
        # ------------------------------------------

        features = attrs.get(
            "feature_values",
            []
        )

        feature_ids = set()

        for feature in features:

            feature_id = feature["feature"].id

            if feature_id in feature_ids:

                raise serializers.ValidationError({
                    "feature_values": (
                        "هر ویژگی فقط یک بار مجاز است."
                    )
                })

            feature_ids.add(
                feature_id
            )

        return attrs


# ==========================================================
# PRODUCT UPDATE
# ==========================================================

class AdminProductUpdateSerializer(serializers.ModelSerializer):

    categories = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        many=True,
        required=False,
    )

    variants = AdminProductVariantInputSerializer(
        many=True,
        required=False,
    )

    feature_values = AdminProductFeatureInputSerializer(
        many=True,
        required=False,
    )

    size_guides = AdminProductSizeGuideInputSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Product

        fields = (
            "title",
            "slug",
            "brief_description",
            "description",
            "categories",
            "status",
            "variants",
            "feature_values",
            "size_guides",
        )

    def validate_title(self, value):

        if Product.objects.filter(
            title=value
        ).exclude(
            pk=self.instance.pk
        ).exists():

            raise serializers.ValidationError(
                "محصولی با این عنوان قبلاً وجود دارد."
            )

        return value

    def validate_slug(self, value):

        if Product.objects.filter(
            slug=value
        ).exclude(
            pk=self.instance.pk
        ).exists():

            raise serializers.ValidationError(
                "محصولی با این اسلاگ قبلاً وجود دارد."
            )

        return value

    def validate(self, attrs):

        # ------------------------------------------
        # VARIANTS
        # ------------------------------------------

        variants = attrs.get(
            "variants"
        )

        if variants is not None:

            combinations = set()
            skus = set()

            for variant in variants:

                combination = (
                    variant["size"].id,
                    variant["color"].id,
                )

                if combination in combinations:

                    raise serializers.ValidationError({
                        "variants": (
                            "ترکیب سایز و رنگ تکراری است."
                        )
                    })

                combinations.add(
                    combination
                )

                sku = variant["sku"]

                if sku in skus:

                    raise serializers.ValidationError({
                        "variants": (
                            f"کد SKU تکراری است: {sku}"
                        )
                    })

                existing = ProductVariant.objects.filter(
                    sku=sku
                ).exclude(
                    product=self.instance
                ).exists()

                if existing:

                    raise serializers.ValidationError({
                        "variants": (
                            f"کد SKU قبلاً استفاده شده است: {sku}"
                        )
                    })

                skus.add(sku)

        # ------------------------------------------
        # FEATURES
        # ------------------------------------------

        features = attrs.get(
            "feature_values"
        )

        if features is not None:

            feature_ids = set()

            for feature in features:

                feature_id = feature["feature"].id

                if feature_id in feature_ids:

                    raise serializers.ValidationError({
                        "feature_values": (
                            "هر ویژگی فقط یک بار مجاز است."
                        )
                    })

                feature_ids.add(
                    feature_id
                )

        return attrs


# ==========================================================
# PRODUCT STATUS
# ==========================================================

class AdminProductStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=ProductStatus.choices
    )


# ==========================================================
# IMAGE UPLOAD
# ==========================================================

class AdminProductImageUploadSerializer(serializers.Serializer):

    image = serializers.ImageField(
        required=True
    )

    is_main = serializers.BooleanField(
        default=False
    )
    
# ==========================================================
# PRODUCT OPTIONS
# ==========================================================

class AdminProductCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "title", "slug", "parent")
        read_only_fields = ("id",)

    def validate_title(self, value):
        if ProductCategory.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "دسته‌بندی با این عنوان قبلاً وجود دارد."
            )
        return value

    def validate_slug(self, value):
        if ProductCategory.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "دسته‌بندی با این اسلاگ قبلاً وجود دارد."
            )
        return value


class AdminProductSizeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ("id", "title")
        read_only_fields = ("id",)

    def validate_title(self, value):
        if ProductSize.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "این سایز قبلاً وجود دارد."
            )
        return value


class AdminProductColorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ("id", "title", "code")
        read_only_fields = ("id",)

    def validate_title(self, value):
        if ProductColor.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "رنگی با این عنوان قبلاً وجود دارد."
            )
        return value

    def validate_code(self, value):
        if ProductColor.objects.filter(code=value).exists():
            raise serializers.ValidationError(
                "این کد رنگ قبلاً استفاده شده است."
            )
        return value


class AdminProductFeatureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "title")
        read_only_fields = ("id",)

    def validate_title(self, value):
        if Feature.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "ویژگی با این عنوان قبلاً وجود دارد."
            )
        return value


# ==========================================================
# PRODUCT OPTIONS RESPONSE
# ==========================================================

class AdminProductOptionsSerializer(serializers.Serializer):
    categories = AdminProductCategorySerializer(many=True)
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    def get_sizes(self, obj):
        return [
            {
                "id": size.id,
                "title": size.title,
            }
            for size in obj["sizes"]
        ]

    def get_colors(self, obj):
        return [
            {
                "id": color.id,
                "title": color.title,
                "code": color.code,
            }
            for color in obj["colors"]
        ]

    def get_features(self, obj):
        return [
            {
                "id": feature.id,
                "title": feature.title,
            }
            for feature in obj["features"]
        ]
        
        
# ==========================================================
# OPTION UPDATE SERIALIZERS
# ==========================================================

class AdminProductCategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "title",
            "slug",
            "parent",
        )
        read_only_fields = ("id",)

    def validate_title(self, value):
        if (
            ProductCategory.objects
            .filter(title=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "دسته‌بندی با این عنوان قبلاً وجود دارد."
            )
        return value

    def validate_slug(self, value):
        if (
            ProductCategory.objects
            .filter(slug=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "دسته‌بندی با این اسلاگ قبلاً وجود دارد."
            )
        return value

    def validate_parent(self, value):
        if value is None:
            return value

        if value.pk == self.instance.pk:
            raise serializers.ValidationError(
                "یک دسته‌بندی نمی‌تواند والد خودش باشد."
            )

        current = value

        while current.parent_id is not None:
            if current.parent_id == self.instance.pk:
                raise serializers.ValidationError(
                    "ایجاد ساختار حلقه‌ای بین دسته‌بندی‌ها مجاز نیست."
                )

            current = current.parent

        return value


class AdminProductSizeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = (
            "id",
            "title",
        )
        read_only_fields = ("id",)

    def validate_title(self, value):
        if (
            ProductSize.objects
            .filter(title=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "این سایز قبلاً وجود دارد."
            )
        return value


class AdminProductColorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = (
            "id",
            "title",
            "code",
        )
        read_only_fields = ("id",)

    def validate_title(self, value):
        if (
            ProductColor.objects
            .filter(title=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "رنگی با این عنوان قبلاً وجود دارد."
            )
        return value

    def validate_code(self, value):
        if (
            ProductColor.objects
            .filter(code=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "این کد رنگ قبلاً استفاده شده است."
            )
        return value


class AdminProductFeatureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = (
            "id",
            "title",
        )
        read_only_fields = ("id",)

    def validate_title(self, value):
        if (
            Feature.objects
            .filter(title=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "ویژگی با این عنوان قبلاً وجود دارد."
            )
        return value
    
# ==========================================================
# OPTION DELETE SERIALIZERS
# ==========================================================

class AdminProductCategoryDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)


class AdminProductSizeDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)


class AdminProductColorDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)


class AdminProductFeatureDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)