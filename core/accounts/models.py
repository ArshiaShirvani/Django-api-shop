from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


# =========================
# User Manager
# =========================
class UserManager(BaseUserManager):
    """مدیریت کاربران با شماره تلفن به‌عنوان شناسه ورود"""

    def create_user(self, phone_number, password=None, role='کاربر', **extra_fields):
        if not phone_number:
            raise ValueError(_("شماره تلفن الزامی است"))

        extra_fields.setdefault('is_active', True)

        user = self.model(
            phone_number=phone_number,
            role=role,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", 'سوپرکاربر')

        if not extra_fields.get("is_staff"):
            raise ValueError(_("سوپرکاربر باید دسترسی staff داشته باشد"))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("سوپرکاربر باید دسترسی superuser داشته باشد"))

        return self.create_user(phone_number, password, **extra_fields)


# =========================
# User Model
# =========================
class User(AbstractBaseUser, PermissionsMixin):

    class Roles(models.TextChoices):
        USER = 'کاربر', _('کاربر')
        ADMIN = 'ادمین', _('ادمین')
        SUPERUSER = 'سوپرکاربر', _('سوپرکاربر')

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="شماره تلفن"
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
        verbose_name="نقش کاربر"
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="دسترسی پنل مدیریت",
        help_text="امکان ورود به پنل مدیریت را مشخص می‌کند"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فعال"
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="شماره تأیید شده",
        help_text="آیا شماره تلفن کاربر تأیید شده است"
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ آخرین بروزرسانی"
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return f"{self.phone_number} - {self.role}"


# =========================
# Profile Model
# =========================
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="کاربر"
    )

    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="نام"
    )

    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="نام خانوادگی"
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def get_fullname(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name if full_name else "کاربر جدید"

    def __str__(self):
        return self.get_fullname()
    
    
class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)

    is_used = models.BooleanField(default=False)

    expires_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)

    attempts = models.PositiveSmallIntegerField(default=0)



# =========================
# Signals
# =========================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
