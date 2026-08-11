from django.contrib import admin
from django.utils.html import format_html

from .models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory,
)



# ==================================
# WEBSITE SETTING
# ==================================

@admin.register(WebsiteSetting)
class WebsiteSettingAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "logo_preview",
        "phone",
        "email",
        "updated_date",
    )


    readonly_fields = (
        "logo_preview",
        "updated_date",
    )


    fieldsets = (

        (
            "اطلاعات اصلی سایت",
            {
                "fields": (
                    "title",
                    "logo",
                    "logo_preview",
                    "description",
                )
            }
        ),


        (
            "اطلاعات تماس",
            {
                "fields": (
                    "phone",
                    "email",
                )
            }
        ),


        (
            "لوکیشن فروشگاه",
            {
                "fields": (
                    "address",
                    "latitude",
                    "longitude",
                )
            }
        ),


        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "updated_date",
                )
            }
        ),

    )


    def logo_preview(self,obj):

        if obj.logo:

            return format_html(
                '<img src="{}" width="120" height="120" style="object-fit:contain;border-radius:10px"/>',
                obj.logo.url
            )

        return "-"


    logo_preview.short_description = "پیش نمایش لوگو"



    # جلوگیری از ساخت چند تنظیمات سایت

    def has_add_permission(self,request):

        if WebsiteSetting.objects.exists():

            return False

        return True





# ==================================
# HOME BANNER
# ==================================

@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):


    list_display = (
        "title",
        "preview",
        "is_active",
        "is_first",
        "order",
        "created_date",
    )


    list_filter = (
        "is_active",
        "is_first",
        "created_date",
    )


    search_fields = (
        "title",
    )


    list_editable = (
        "is_active",
        "is_first",
        "order",
    )


    readonly_fields = (
        "preview",
        "created_date",
        "updated_date",
    )


    ordering = (
        "order",
    )



    fieldsets = (

        (
            "اطلاعات بنر",
            {
                "fields": (
                    "title",
                    "image",
                    "preview",
                    "link",
                )
            }
        ),


        (
            "تنظیمات نمایش",
            {
                "fields": (
                    "is_active",
                    "is_first",
                    "order",
                )
            }
        ),


        (
            "تاریخ ها",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            }
        ),

    )



    def preview(self,obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="250" height="100" style="object-fit:cover;border-radius:10px"/>',
                obj.image.url
            )

        return "-"


    preview.short_description = "پیش نمایش"





# ==================================
# SECONDARY BANNER
# ==================================


@admin.register(SecondaryBanner)
class SecondaryBannerAdmin(admin.ModelAdmin):


    list_display = (
        "title",
        "preview",
        "is_active",
        "order",
        "created_date",
    )


    list_filter = (
        "is_active",
        "created_date",
    )


    search_fields = (
        "title",
    )


    list_editable = (
        "is_active",
        "order",
    )


    readonly_fields = (
        "preview",
        "created_date",
        "updated_date",
    )


    ordering = (
        "order",
    )



    fieldsets = (

        (
            "اطلاعات بنر",
            {
                "fields": (
                    "title",
                    "image",
                    "preview",
                    "link",
                )
            }
        ),


        (
            "تنظیمات نمایش",
            {
                "fields": (
                    "is_active",
                    "order",
                )
            }
        ),


        (
            "تاریخ ها",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            }
        ),

    )


    def preview(self,obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="300" height="120" style="object-fit:cover;border-radius:10px"/>',
                obj.image.url
            )

        return "-"


    preview.short_description = "پیش نمایش"





# ==================================
# HOME CATEGORY
# ==================================


@admin.register(HomeCategory)
class HomeCategoryAdmin(admin.ModelAdmin):


    list_display = (
        "category",
        "preview",
        "custom_title",
        
        "is_active",
    )


    list_filter = (
        "is_active",
    )


    search_fields = (
        "category__title",
        "custom_title",
    )


    list_editable = (
        
        "is_active",
    )


    readonly_fields = (
        "preview",
        "created_date",
        "updated_date",
    )


    



    fieldsets = (

        (
            "دسته بندی",
            {
                "fields": (
                    "category",
                    "custom_title",
                )
            }
        ),


        (
            "تصویر و نمایش",
            {
                "fields": (
                    "image",
                    "preview",
                    
                    "is_active",
                )
            }
        ),


        (
            "تاریخ ها",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            }
        ),

    )



    def preview(self,obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:50%"/>',
                obj.image.url
            )

        return "-"


    preview.short_description = "تصویر"