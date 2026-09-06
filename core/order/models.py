from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from accounts.models import User
from shop.models import ProductVariant


# =========================================================
# ORDER STATUS
# =========================================================

class OrderStatus(models.TextChoices):

    PENDING = "pending", "در انتظار پرداخت"
    PAID = "paid", "پرداخت شده"
    PROCESSING = "processing", "در حال پردازش"
    SHIPPED = "shipped", "ارسال شده"
    DELIVERED = "delivered", "تحویل داده شده"
    CANCELLED = "cancelled", "لغو شده"


# =========================================================
# ADDRESS
# =========================================================

class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="کاربر",
    )

    title = models.CharField(
        max_length=100,
        verbose_name="عنوان آدرس",
        help_text="مثلاً خانه، محل کار",
    )

    recipient_name = models.CharField(
        max_length=255,
        verbose_name="نام گیرنده",
    )

    recipient_phone = models.CharField(
        max_length=11,
        verbose_name="شماره تلفن گیرنده",
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
                fields=["user"]
            ),
            models.Index(
                fields=["is_default"]
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

        return (
            f"{self.title} - "
            f"{self.recipient_name}"
        )


# =========================================================
# SHIPPING METHOD
# =========================================================

class ShippingMethod(models.Model):

    title = models.CharField(
        max_length=100,
        verbose_name="عنوان",
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name="کد",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    base_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه ارسال",
    )

    free_shipping_minimum = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="حداقل مبلغ ارسال رایگان",
        help_text="خالی = ارسال رایگان خودکار وجود ندارد",
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
                fields=["is_active"]
            ),
            models.Index(
                fields=["display_order"]
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
# COUPON
# =========================================================

class Coupon(models.Model):

    class DiscountType(models.TextChoices):

        PERCENTAGE = (
            "percentage",
            "درصدی"
        )

        FIXED = (
            "fixed",
            "مبلغ ثابت"
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
            MinValueValidator(1)
        ],
        verbose_name="مقدار تخفیف",
    )

    max_discount_amount = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="حداکثر مبلغ تخفیف",
    )

    minimum_order_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="حداقل مبلغ سفارش",
    )

    start_date = models.DateTimeField(
        verbose_name="تاریخ شروع",
    )

    end_date = models.DateTimeField(
        verbose_name="تاریخ پایان",
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="محدودیت استفاده کل",
        help_text="خالی = بدون محدودیت",
    )

    usage_limit_per_user = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name="محدودیت استفاده هر کاربر",
    )

    is_global = models.BooleanField(
        default=True,
        verbose_name="کد همگانی",
        help_text="اگر خاموش باشد فقط کاربران انتخاب‌شده مجاز هستند.",
    )

    users = models.ManyToManyField(
        User,
        blank=True,
        related_name="assigned_coupons",
        verbose_name="کاربران مجاز",
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
            "-created_date"
        ]

        indexes = [
            models.Index(
                fields=["code"]
            ),
            models.Index(
                fields=["is_active"]
            ),
            models.Index(
                fields=[
                    "start_date",
                    "end_date",
                ]
            ),
        ]

    def clean(self):

        self.code = self.code.strip().upper()

        if self.start_date and self.end_date:

            if self.start_date >= self.end_date:

                raise ValidationError(
                    "تاریخ شروع باید قبل از تاریخ پایان باشد."
                )

        if self.discount_type == self.DiscountType.PERCENTAGE:

            if self.discount_value > 100:

                raise ValidationError(
                    "درصد تخفیف نمی‌تواند بیشتر از 100 باشد."
                )

        if (
            self.discount_type == self.DiscountType.FIXED
            and self.max_discount_amount is not None
        ):

            raise ValidationError(
                "حداکثر مبلغ تخفیف فقط برای تخفیف درصدی قابل استفاده است."
            )

    def save(self, *args, **kwargs):

        self.code = self.code.strip().upper()

        self.full_clean()

        super().save(*args, **kwargs)

    @property
    def is_valid_time(self):

        now = timezone.now()

        return (
            self.is_active
            and self.start_date <= now
            and self.end_date >= now
        )

    def is_available_for_user(self, user):

        if not self.is_valid_time:
            return False

        # کد اختصاصی
        if not self.is_global:

            if not self.users.filter(
                pk=user.pk
            ).exists():

                return False

        # محدودیت استفاده کل
        if self.usage_limit is not None:

            total_usage = self.usages.count()

            if total_usage >= self.usage_limit:
                return False

        # محدودیت استفاده کاربر
        user_usage = self.usages.filter(
            user=user
        ).count()

        if user_usage >= self.usage_limit_per_user:
            return False

        return True

    def calculate_discount(self, subtotal):

        if subtotal < self.minimum_order_amount:
            return 0

        if self.discount_type == self.DiscountType.PERCENTAGE:

            discount = (
                subtotal * self.discount_value
            ) // 100

            if self.max_discount_amount is not None:

                discount = min(
                    discount,
                    self.max_discount_amount
                )

        else:

            discount = self.discount_value

        return min(
            discount,
            subtotal
        )

    def __str__(self):

        return self.code


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="وضعیت سفارش",
    )

    # =====================================================
    # PRICE
    # =====================================================

    subtotal = models.PositiveBigIntegerField(
        default=0,
        verbose_name="جمع محصولات",
    )

    tax = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مالیات",
    )

    discount = models.PositiveBigIntegerField(
        default=0,
        verbose_name="تخفیف",
    )

    shipping_cost = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه ارسال",
    )

    total = models.PositiveBigIntegerField(
        default=0,
        verbose_name="مبلغ نهایی",
    )

    # =====================================================
    # COUPON
    # =====================================================

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="کد تخفیف",
    )

    # =====================================================
    # SHIPPING
    # =====================================================

    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="روش ارسال",
    )

    # =====================================================
    # ADDRESS SNAPSHOT
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
        verbose_name="آدرس",
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
    # TRACKING
    # =====================================================

    tracking_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="کد پیگیری",
    )

    # =====================================================
    # DATES
    # =====================================================

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
            "-created_date"
        ]

        indexes = [
            models.Index(
                fields=["user"]
            ),
            models.Index(
                fields=["status"]
            ),
            models.Index(
                fields=["created_date"]
            ),
            models.Index(
                fields=["tracking_code"]
            ),
        ]

    @property
    def is_paid(self):

        return self.status in [
            OrderStatus.PAID,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        ]

    @property
    def payable_amount(self):

        return max(
            self.total,
            0
        )

    def calculate_tax(self):

        taxable_amount = max(
            self.subtotal - self.discount,
            0
        )

        return (
            taxable_amount * 10
        ) // 100

    def calculate_total(self):
        return (
            max(self.subtotal - self.discount, 0)
            + self.tax
            + self.shipping_cost
        )

    def update_totals(self):

        self.subtotal = sum(
            item.subtotal
            for item in self.items.all()
        )

        self.tax = self.calculate_tax()

        self.total = self.calculate_total()

    def __str__(self):

        return (
            f"سفارش #{self.pk} - "
            f"{self.user.phone_number}"
        )


# =========================================================
# ORDER ITEM
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
    # PRODUCT SNAPSHOT
    # =====================================================

    product_title = models.CharField(
        max_length=200,
        verbose_name="نام محصول",
    )

    size = models.CharField(
        max_length=50,
        verbose_name="سایز",
    )

    color = models.CharField(
        max_length=50,
        verbose_name="رنگ",
    )

    sku = models.CharField(
        max_length=50,
        verbose_name="کد انبار",
    )

    # =====================================================
    # PRICE SNAPSHOT
    # =====================================================

    unit_price = models.PositiveBigIntegerField(
        verbose_name="قیمت واحد",
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ],
        verbose_name="تعداد",
    )

    subtotal = models.PositiveBigIntegerField(
        default=0,
        verbose_name="جمع",
    )

    class Meta:

        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

        ordering = [
            "id"
        ]

        indexes = [
            models.Index(
                fields=["order"]
            ),
            models.Index(
                fields=["variant"]
            ),
        ]

    def calculate_subtotal(self):

        return (
            self.unit_price *
            self.quantity
        )

    def save(self, *args, **kwargs):

        self.subtotal = self.calculate_subtotal()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.product_title} - "
            f"{self.quantity}"
        )


# =========================================================
# COUPON USAGE
# =========================================================

class CouponUsage(models.Model):

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.PROTECT,
        related_name="usages",
        verbose_name="کد تخفیف",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="coupon_usages",
        verbose_name="کاربر",
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="coupon_usage",
        verbose_name="سفارش",
    )

    used_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ استفاده",
    )

    class Meta:

        verbose_name = "استفاده از کد تخفیف"
        verbose_name_plural = "استفاده‌های کد تخفیف"

        ordering = [
            "-used_date"
        ]

        indexes = [
            models.Index(
                fields=["coupon"]
            ),
            models.Index(
                fields=["user"]
            ),
            models.Index(
                fields=["used_date"]
            ),
        ]

    def __str__(self):

        return (
            f"{self.coupon.code} - "
            f"{self.user.phone_number}"
        )