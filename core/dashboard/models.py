from django.db import models

from accounts.models import User
from shop.models import Product


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="کاربر",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="محصول",
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن",
    )

    class Meta:
        verbose_name = "محصول مورد علاقه"
        verbose_name_plural = "محصولات مورد علاقه"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_favorite_product",
            )
        ]

        indexes = [
            models.Index(
                fields=["user", "-created_date"],
                name="favorite_user_created_idx",
            ),
        ]

        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.user.phone_number} - {self.product.title}"