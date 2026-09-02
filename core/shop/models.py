from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ===========================
# Product Status
# ===========================

class ProductStatus(models.IntegerChoices):
    PUBLISHED = 1, "فعال"
    DRAFT = 2, "غیرفعال"


# ===========================
# Category
# ===========================

class ProductCategory(models.Model):
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="عنوان دسته بندی"
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ"
    )

    image = models.ImageField(
        upload_to="shop/categories/images/",
        null=True,
        blank=True,
        verbose_name="تصویر"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته بندی والد"
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"

        ordering = ["title"]

        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_root(self):
        return self.parent_id is None


# ===========================
# Feature
# ===========================

class Feature(models.Model):

    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="عنوان ویژگی"
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی ها"

        ordering = ["title"]

    def __str__(self):
        return self.title


# ===========================
# Product
# ===========================

class Product(models.Model):

    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="عنوان محصول"
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ"
    )

    brief_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="توضیح کوتاه"
    )

    description = models.TextField(
        verbose_name="توضیحات کامل"
    )

    categories = models.ManyToManyField(
        ProductCategory,
        related_name="products",
        verbose_name="دسته بندی ها"
    )

    status = models.IntegerField(
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
        verbose_name="وضعیت"
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "محصول"

        verbose_name_plural = "محصولات"

        ordering = ["-created_date"]

        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_date"]),
        ]

    def __str__(self):
        return self.title

    @property
    def main_image(self):
        images = list(self.images.all())

        for image in images:
            if image.is_main:
                return image

        return images[0] if images else None

    @property
    def active_variants(self):
        """
        تنوع‌های فعال و دارای موجودی
        """
        return self.variants.filter(
            is_active=True,
            stock__gt=0
        )

    @property
    def has_stock(self):
        return self.active_variants.exists()

    @property
    def min_price(self):
        variant = self.active_variants.order_by(
            "price"
        ).first()

        if variant:
            return variant.final_price

        return None

    @property
    def max_discount(self):
        variant = self.active_variants.order_by(
            "-discount_percent"
        ).first()

        if variant:
            return variant.discount_percent

        return 0
    
# ===========================
# Product Size
# ===========================

class ProductSize(models.Model):

    title = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="عنوان"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سایز محصول"
        verbose_name_plural = "سایز محصولات"

        ordering = ["title"]

    def __str__(self):
        return self.title


# ===========================
# Product Color
# ===========================

class ProductColor(models.Model):

    title = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="عنوان"
    )

    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="کد رنگ"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "رنگ محصول"
        verbose_name_plural = "رنگ محصولات"

        ordering = ["title"]

    def __str__(self):
        return self.title


# ===========================
# Product Images
# ===========================

class ProductImages(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="محصول"
    )

    image = models.ImageField(
        upload_to="shop/products/images/",
        verbose_name="تصویر"
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name="تصویر اصلی"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:

        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

        ordering = ["-is_main", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_main=True),
                name="unique_main_product_image"
            )
        ]

    def save(self, *args, **kwargs):

        if self.is_main:

            ProductImages.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(
                pk=self.pk
            ).update(
                is_main=False
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.title}"


# ===========================
# Product Variant
# ===========================

class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="محصول"
    )

    size = models.ForeignKey(
        ProductSize,
        on_delete=models.PROTECT,
        verbose_name="سایز"
    )

    color = models.ForeignKey(
        ProductColor,
        on_delete=models.PROTECT,
        verbose_name="رنگ"
    )

    price = models.PositiveBigIntegerField(
        verbose_name="قیمت"
    )

    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        verbose_name="درصد تخفیف"
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد انبار"
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:

        verbose_name = "تنوع محصول"
        verbose_name_plural = "تنوع محصولات"

        ordering = ["price"]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "product",
                    "size",
                    "color"
                ],
                name="unique_product_variant"
            ),

            models.CheckConstraint(
                check=models.Q(
                    discount_percent__gte=0,
                    discount_percent__lte=100
                ),
                name="discount_between_0_100"
            )

        ]

        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["stock"]),
        ]

    @property
    def final_price(self):

        price = self.price or 0
        discount = self.discount_percent or 0

        return (
            price *
            (100 - discount)
        ) // 100

    @property
    def has_discount(self):

        return self.discount_percent > 0

    @property
    def is_available(self):

        return self.is_active and self.stock > 0

    def __str__(self):

        return (
            f"{self.product.title}"
            f" | {self.color.title}"
            f" | {self.size.title}"
        )


# ===========================
# Feature Value
# ===========================

class FeatureValue(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="feature_values",
        verbose_name="محصول"
    )

    feature = models.ForeignKey(
        Feature,
        on_delete=models.PROTECT,
        verbose_name="ویژگی"
    )

    value = models.CharField(
        max_length=255,
        verbose_name="مقدار"
    )

    class Meta:

        verbose_name = "مشخصات محصول"

        verbose_name_plural = "مشخصات محصولات"

        ordering = ["feature__title"]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "product",
                    "feature"
                ],
                name="unique_product_feature"
            )

        ]

    def __str__(self):

        return f"{self.product.title} - {self.feature.title}"
    
    
class SizeGuide(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="size_guides",
        verbose_name="محصول"
    )

    feature = models.CharField(
        max_length=255,
        verbose_name="ویژگی",
        blank=True,
        null=True,
    )

    value = models.CharField(
        max_length=255,
        verbose_name="مقدار",
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to="shop/size_guides/",
        null=True,
        blank=True,
        verbose_name="تصویر"
    )

    class Meta:
        verbose_name = "راهنمای سایز"
        verbose_name_plural = "راهنمای سایز"

    def __str__(self):
        return f"{self.product.title} - {self.feature}"