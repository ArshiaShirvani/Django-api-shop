from django.db import models
from django.core.exceptions import ValidationError

from shop.models import ProductCategory



# ==========================
# WEBSITE SETTINGS
# ==========================

class WebsiteSetting(models.Model):

    title = models.CharField(
        max_length=200,
        default="Website",
        verbose_name="عنوان سایت"
    )

    logo = models.ImageField(
        upload_to="website/settings/logo/",
        null=True,
        blank=True,
        verbose_name="لوگو"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )


    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس"
    )


    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل"
    )


    address = models.TextField(
        blank=True,
        verbose_name="آدرس فروشگاه"
    )


    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="عرض جغرافیایی"
    )


    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="طول جغرافیایی"
    )

    created_date = models.DateTimeField(
            auto_now_add=True,
            verbose_name="تاریخ ایجاد"
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )


    def __str__(self):
        return self.title


    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"





# ==========================
# HOME BANNER
# ==========================


class HomeBanner(models.Model):

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان"
    )


    image = models.ImageField(
        upload_to="website/banners/",
        verbose_name="تصویر"
    )


    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک"
    )


    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )


    is_first = models.BooleanField(
        default=False,
        verbose_name="بنر اول"
    )


    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب"
    )


    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )


    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )



    def clean(self):

        # فقط یک بنر اول
        if self.is_first:

            exists = HomeBanner.objects.filter(
                is_first=True
            ).exclude(
                pk=self.pk
            ).exists()


            if exists:
                raise ValidationError(
                    "فقط یک بنر می‌تواند بنر اول باشد."
                )



        # حداکثر ۴ بنر فعال
        if self.is_active:

            count = HomeBanner.objects.filter(
                is_active=True
            ).exclude(
                pk=self.pk
            ).count()


            if count >= 4:

                raise ValidationError(
                    "حداکثر ۴ بنر اصلی می‌تواند فعال باشد."
                )



    def save(self,*args,**kwargs):

        if self.is_first:

            self.order = 1
            self.is_active = True


        self.full_clean()

        super().save(*args,**kwargs)



    def __str__(self):

        return self.title



    class Meta:

        ordering = [
            "order",
            "-id"
        ]

        verbose_name = "بنر اصلی"
        verbose_name_plural = "بنرهای اصلی"





# ==========================
# SECONDARY BANNER
# ==========================


class SecondaryBanner(models.Model):


    title = models.CharField(
        max_length=200,
        verbose_name="عنوان"
    )


    image = models.ImageField(
        upload_to="website/banner/secondary/",
        verbose_name="تصویر"
    )


    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک"
    )


    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )


    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب"
    )


    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )


    updated_date = models.DateTimeField(
        auto_now=True
    )



    def clean(self):

        if self.is_active:

            exists = SecondaryBanner.objects.filter(
                is_active=True
            ).exclude(
                pk=self.pk
            ).exists()


            if exists:

                raise ValidationError(
                    "فقط یک بنر ثانویه می‌تواند فعال باشد."
                )



    def save(self,*args,**kwargs):

        self.full_clean()

        super().save(*args,**kwargs)



    def __str__(self):

        return self.title



    class Meta:

        ordering = [
            "order",
            "-id"
        ]

        verbose_name = "بنر ثانویه"
        verbose_name_plural = "بنرهای ثانویه"





# ==========================
# HOME CATEGORY
# ==========================


class HomeCategory(models.Model):

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="home_categories",
        verbose_name="دسته بندی"
    )

    custom_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="عنوان نمایشی"
    )

    image = models.ImageField(
        upload_to="website/categories/",
        null=True,
        blank=True,
        verbose_name="تصویر"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )


    def clean(self):

        if self.is_active:

            count = HomeCategory.objects.filter(
                is_active=True
            ).exclude(
                pk=self.pk
            ).count()


            if count >= 5:

                raise ValidationError(
                    "حداکثر ۵ دسته در صفحه اصلی فعال باشد."
                )


    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)


    def __str__(self):

        return self.custom_title or self.category.title


    class Meta:


        verbose_name = "دسته صفحه اصلی"
        verbose_name_plural = "دسته های صفحه اصلی"
        
        
from django.db import models


# ==========================================
# CONTACT MODEL
# ==========================================

class ContactMessage(models.Model):

    name = models.CharField(
        max_length=100
    )

    subject = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    message = models.TextField()

    seen = models.BooleanField(
        default=False
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-created_date"
        ]

        verbose_name = "تیکت تماس با ما"

        verbose_name_plural = "تیکت تماس با ما"

    def __str__(self):
        return f"{self.name} - {self.subject}"