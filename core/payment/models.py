from django.db import models

from accounts.models import User
from order.models import Order


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "در انتظار پرداخت"
    SUCCESS = "success", "موفق"
    FAILED = "failed", "ناموفق"
    CANCELED = "canceled", "لغو شده"


class PaymentGateway(models.TextChoices):
    ZARINPAL = "zarinpal", "زرین پال"


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="سفارش",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="کاربر",
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ پرداخت",
    )

    currency = models.CharField(
        max_length=10,
        default="IRR",
        verbose_name="واحد پول",
    )

    gateway = models.CharField(
        max_length=50,
        choices=PaymentGateway.choices,
        default=PaymentGateway.ZARINPAL,
        verbose_name="درگاه پرداخت",
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="وضعیت پرداخت",
    )

    authority = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name="شناسه Authority",
    )

    reference_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="شماره مرجع تراکنش",
    )

    gateway_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات درگاه",
    )

    error_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="کد خطای درگاه",
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="پیام خطای درگاه",
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
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداختها"

        indexes = [
            models.Index(
                fields=["user", "status"],
                name="payment_user_status_idx",
            ),
            models.Index(
                fields=["order", "status"],
                name="payment_order_status_idx",
            ),
            models.Index(
                fields=["gateway", "status"],
                name="payment_gateway_status_idx",
            ),
            models.Index(
                fields=["created_date"],
                name="payment_created_idx",
            ),
        ]

        ordering = ["-created_date"]

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order_id}"

    @property
    def is_success(self):
        return self.status == PaymentStatus.SUCCESS