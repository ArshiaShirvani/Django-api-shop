from decimal import Decimal
import uuid

from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone

from shop.models import ProductVariant


# =========================================================
# Address
# =========================================================

class Address(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="کاربر",
    )

    title = models.CharField(
        max_length=100,
        verbose_name="عنوان آدرس",
        help_text="مثلاً خانه، محل کار و ...",
    )

    recipient_name = models.CharField(
        max_length=255,
        verbose_name="نام گیرنده",
    )

    recipient_phone = models.CharField(
        max_length=11,
        verbose_name="شماره تماس گیرنده",
    )

    province = models.CharField(
        max_length=100,
        verbose_name="استان",
    )

    city = models.CharField(
        max_length=100,
        verbose_name="شهر",
    )

    address = models.TextField(
        verbose_name="آدرس کامل",
    )

    postal_code = models.CharField(
        max_length=10,
        verbose_name="کد پستی",
    )

    plaque = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="پلاک",
    )

    unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="واحد",
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="آدرس پیش‌فرض",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

        ordering = [
            "-is_default",
            "-created_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "user",
                    "is_default",
                ]
            ),
        ]

    def save(self, *args, **kwargs):

        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True,
            ).exclude(
                pk=self.pk
            ).update(
                is_default=False
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.recipient_name}"


# =========================================================
# Shipping Method
# =========================================================

class ShippingMethod(models.Model):

    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="عنوان روش ارسال",
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name="کد روش ارسال",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    base_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه پایه ارسال",
    )

    free_shipping_minimum = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="حداقل مبلغ برای ارسال رایگان",
        help_text="خالی = ارسال رایگان فعال نیست",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        verbose_name = "روش ارسال"
        verbose_name_plural = "روش‌های ارسال"

        ordering = [
            "display_order",
            "id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "is_active",
                    "display_order",
                ]
            ),
        ]

    def calculate_cost(self, subtotal):

        if (
            self.free_shipping_minimum is not None
            and subtotal >= self.free_shipping_minimum
        ):
            return 0

        return self.base_cost

    def __str__(self):
        return self.title


# =========================================================
# Coupon
# =========================================================

class Coupon(models.Model):

    class DiscountType(models.TextChoices):

        PERCENTAGE = (
            "percentage",
            "درصدی",
        )

        FIXED = (
            "fixed",
            "مبلغ ثابت",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تخفیف",
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        verbose_name="نوع تخفیف",
    )

    discount_value = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="مقدار تخفیف",
        help_text=(
            "برای درصدی = درصد تخفیف / "
            "برای ثابت = مبلغ"
        ),
    )

    max_discount_amount = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="حداکثر مبلغ تخفیف",
        help_text="فقط برای تخفیف درصدی",
    )

    minimum_order_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="حداقل مبلغ سفارش",
    )

    start_date = models.DateTimeField(
        verbose_name="تاریخ و ساعت شروع",
    )

    end_date = models.DateTimeField(
        verbose_name="تاریخ و ساعت پایان",
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="حداکثر تعداد استفاده",
        help_text="خالی = بدون محدودیت",
    )

    usage_limit_per_user = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="حداکثر استفاده هر کاربر",
    )

    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="available_coupons",
        verbose_name="کاربران مجاز",
        help_text=(
            "اگر خالی باشد، کد تخفیف عمومی است "
            "و همه کاربران می‌توانند از آن استفاده کنند."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

        ordering = [
            "-created_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "code",
                ]
            ),
            models.Index(
                fields=[
                    "is_active",
                    "start_date",
                    "end_date",
                ]
            ),
        ]

    def save(self, *args, **kwargs):

        self.code = self.code.strip().upper()

        super().save(*args, **kwargs)

    @property
    def is_valid_time(self):

        now = timezone.now()

        return (
            self.is_active
            and self.start_date <= now
            and self.end_date >= now
        )

    @property
    def is_public(self):
        return not self.allowed_users.exists()

    def is_available_for_user(self, user):

        if not self.allowed_users.exists():
            return True

        return self.allowed_users.filter(
            pk=user.pk
        ).exists()

    def calculate_discount(self, subtotal):

        if subtotal < self.minimum_order_amount:
            return 0

        if self.discount_type == self.DiscountType.PERCENTAGE:

            discount = (
                Decimal(subtotal)
                * Decimal(self.discount_value)
                / Decimal(100)
            )

            discount = int(discount)

            if self.max_discount_amount is not None:
                discount = min(
                    discount,
                    self.max_discount_amount,
                )

            return max(
                discount,
                0,
            )

        if self.discount_type == self.DiscountType.FIXED:

            return min(
                self.discount_value,
                subtotal,
            )

        return 0

    def __str__(self):
        return self.code


# =========================================================
# Coupon Usage
# =========================================================

class CouponUsage(models.Model):

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.PROTECT,
        related_name="usages",
        verbose_name="کد تخفیف",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coupon_usages",
        verbose_name="کاربر",
    )

    order = models.OneToOneField(
        "Order",
        on_delete=models.PROTECT,
        related_name="coupon_usage",
        verbose_name="سفارش",
    )

    discount_amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ تخفیف",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ استفاده",
    )

    class Meta:
        verbose_name = "استفاده از کد تخفیف"
        verbose_name_plural = "استفاده‌های کد تخفیف"

        ordering = [
            "-created_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "coupon",
                    "user",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.coupon.code} - "
            f"{self.user}"
        )


# =========================================================
# Order
# =========================================================

class Order(models.Model):

    class Status(models.IntegerChoices):

        PENDING = 1, "در انتظار پرداخت"
        PAID = 2, "پرداخت شده"
        PROCESSING = 3, "در حال پردازش"
        READY_TO_SHIP = 4, "آماده ارسال"
        SHIPPED = 5, "ارسال شده"
        DELIVERED = 6, "تحویل داده شده"
        CANCELLED = 7, "لغو شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )

    order_number = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        verbose_name="شماره سفارش",
    )

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت سفارش",
    )

    # =====================================================
    # Coupon
    # =====================================================

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="کد تخفیف",
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد تخفیف استفاده شده",
    )

    coupon_discount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ تخفیف کد",
    )

    # =====================================================
    # Shipping
    # =====================================================

    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="روش ارسال",
    )

    shipping_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="عنوان روش ارسال",
    )

    shipping_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه ارسال",
    )

    # =====================================================
    # Address Snapshot
    # =====================================================

    recipient_name = models.CharField(
        max_length=255,
        verbose_name="نام گیرنده",
    )

    recipient_phone = models.CharField(
        max_length=11,
        verbose_name="شماره گیرنده",
    )

    province = models.CharField(
        max_length=100,
        verbose_name="استان",
    )

    city = models.CharField(
        max_length=100,
        verbose_name="شهر",
    )

    address = models.TextField(
        verbose_name="آدرس کامل",
    )

    postal_code = models.CharField(
        max_length=10,
        verbose_name="کد پستی",
    )

    plaque = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="پلاک",
    )

    unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="واحد",
    )

    # =====================================================
    # Price
    # =====================================================

    subtotal = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ کالاها",
    )

    discount_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مجموع تخفیف",
    )

    total_price = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ نهایی",
    )

    # =====================================================
    # Payment
    # =====================================================

    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="شناسه پرداخت",
    )

    # =====================================================
    # Shipping Tracking
    # =====================================================

    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="کد پیگیری مرسوله",
    )

    # =====================================================
    # Dates
    # =====================================================

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ پرداخت",
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ارسال",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تحویل",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ لغو",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

        ordering = [
            "-created_date",
        ]

        indexes = [
            models.Index(
                fields=[
                    "user",
                    "-created_date",
                ]
            ),
            models.Index(
                fields=[
                    "status",
                ]
            ),
            models.Index(
                fields=[
                    "order_number",
                ]
            ),
            models.Index(
                fields=[
                    "coupon_code",
                ]
            ),
        ]

    def save(self, *args, **kwargs):

        if not self.order_number:
            self.order_number = (
                f"ORD-{uuid.uuid4().hex[:20].upper()}"
            )

        super().save(
            *args,
            **kwargs
        )

    @property
    def is_paid(self):

        return self.status in [
            self.Status.PAID,
            self.Status.PROCESSING,
            self.Status.READY_TO_SHIP,
            self.Status.SHIPPED,
            self.Status.DELIVERED,
        ]

    @property
    def is_cancelled(self):

        return (
            self.status ==
            self.Status.CANCELLED
        )


# =========================================================
# Order Item
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="تنوع محصول",
    )

    # =====================================================
    # Product Snapshot
    # =====================================================

    product_title = models.CharField(
        max_length=255,
        verbose_name="عنوان محصول",
    )

    sku = models.CharField(
        max_length=50,
        verbose_name="کد انبار",
    )

    size = models.CharField(
        max_length=50,
        verbose_name="سایز",
    )

    color = models.CharField(
        max_length=100,
        verbose_name="رنگ",
    )

    color_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="کد رنگ",
    )

    # =====================================================
    # Price Snapshot
    # =====================================================

    original_unit_price = models.PositiveBigIntegerField(
        verbose_name="قیمت اصلی واحد",
    )

    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        verbose_name="درصد تخفیف محصول",
    )

    unit_price = models.PositiveBigIntegerField(
        verbose_name="قیمت نهایی واحد",
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="تعداد",
    )

    subtotal = models.PositiveBigIntegerField(
        verbose_name="جمع",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

        ordering = [
            "id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "order",
                ]
            ),
            models.Index(
                fields=[
                    "variant",
                ]
            ),
            models.Index(
                fields=[
                    "sku",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.product_title} - "
            f"{self.quantity}"
        )