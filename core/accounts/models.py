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
    """
    Custom user model manager where phone_number is the unique identifier
    for authentication instead of email/usernames.
    """

    def create_user(self, phone_number, password=None, role='کاربر', **extra_fields):
        if not phone_number:
            raise ValueError(_("لطفاً شماره تلفن را وارد کنید"))
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", 'سوپرکاربر')

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("سوپرکاربر باید is_staff=True داشته باشد."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("سوپرکاربر باید is_superuser=True داشته باشد."))
        return self.create_user(phone_number, password, **extra_fields)


# =========================
# User Model
# =========================
class User(AbstractBaseUser, PermissionsMixin):

    class Roles(models.TextChoices):
        USER = 'کاربر', _('کاربر')
        ADMIN = 'ادمین', _('ادمین')
        SUPERUSER = 'سوپرکاربر', _('سوپرکاربر')

    phone_number = models.CharField("شماره تلفن", max_length=15, unique=True, verbose_name="شماره تلفن")
    role = models.CharField(
        "نقش", max_length=20, choices=Roles.choices, default=Roles.USER, verbose_name="نقش کاربر"
    )
    is_staff = models.BooleanField("عضو تیم مدیریتی", default=False, help_text="تعیین می‌کند آیا کاربر می‌تواند وارد admin شود.")
    is_active = models.BooleanField("فعال", default=True, help_text="تعیین می‌کند حساب کاربر فعال است یا خیر.")
    is_verified = models.BooleanField("تأیید شده", default=False, help_text="تعیین می‌کند شماره تلفن کاربر تأیید شده است یا خیر.")

    created_date = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_date = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.phone_number} ({self.role})"


# =========================
# Profile Model
# =========================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="کاربر")
    first_name = models.CharField("نام", max_length=255, blank=True, null=True, verbose_name="نام")
    last_name = models.CharField("نام خانوادگی", max_length=255, blank=True, null=True, verbose_name="نام خانوادگی")
    created_date = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_date = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    def get_fullname(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name if full_name else "کاربر جدید"

    def __str__(self):
        return self.get_fullname()


# =========================
# Signals
# =========================
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
