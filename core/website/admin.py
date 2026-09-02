from django.contrib import admin
from django.utils.html import format_html

from .models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory,
    ContactMessage,
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
                    "phone_bannner",
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


# ==========================================
# CONTACT MESSAGE ADMIN
# ==========================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    # --------------------------------------
    # LIST DISPLAY
    # --------------------------------------

    list_display = (
        "name",
        "subject",
        "phone",
        "email",
        "seen_status",
        "created_date",
    )

    # --------------------------------------
    # LIST FILTER
    # --------------------------------------

    list_filter = (
        "seen",
        "created_date",
    )

    # --------------------------------------
    # SEARCH
    # --------------------------------------

    search_fields = (
        "name",
        "subject",
        "phone",
        "email",
        "message",
    )

    # --------------------------------------
    # DATE HIERARCHY
    # --------------------------------------

    date_hierarchy = "created_date"

    # --------------------------------------
    # DEFAULT ORDER
    # --------------------------------------

    ordering = (
        "seen",
        "-created_date",
    )

    # --------------------------------------
    # READ ONLY
    # --------------------------------------

    readonly_fields = (
        "created_date",
    )

    # --------------------------------------
    # ITEMS PER PAGE
    # --------------------------------------

    list_per_page = 25

    # --------------------------------------
    # CLICKABLE ROW
    # --------------------------------------

    list_display_links = (
        "name",
        "subject",
    )

    # --------------------------------------
    # FORM LAYOUT
    # --------------------------------------

    fieldsets = (

        (
            "اطلاعات تماس",
            {
                "fields": (
                    "name",
                    "phone",
                    "email",
                )
            }
        ),

        (
            "پیام",
            {
                "fields": (
                    "subject",
                    "message",
                )
            }
        ),

        (
            "وضعیت",
            {
                "fields": (
                    "seen",
                    "created_date",
                )
            }
        ),

    )

    # --------------------------------------
    # SEEN STATUS
    # --------------------------------------

    @admin.display(
        description="وضعیت",
        ordering="seen"
    )
    def seen_status(self, obj):

        if obj.seen:

            return format_html(
                '<span style="'
                'background:#dcfce7;'
                'color:#166534;'
                'padding:5px 10px;'
                'border-radius:8px;'
                'font-weight:600;'
                '">'
                '✓ خوانده شده'
                '</span>'
            )

        return format_html(
            '<span style="'
            'background:#fee2e2;'
            'color:#991b1b;'
            'padding:5px 10px;'
            'border-radius:8px;'
            'font-weight:600;'
            '">'
            '● خوانده نشده'
            '</span>'
        )

    # --------------------------------------
    # ACTIONS
    # --------------------------------------

    actions = (
        "mark_as_seen",
        "mark_as_unseen",
    )

    @admin.action(
        description="علامت‌گذاری پیام‌های انتخاب‌شده به عنوان خوانده‌شده"
    )
    def mark_as_seen(self, request, queryset):

        updated = queryset.update(
            seen=True
        )

        self.message_user(
            request,
            f"{updated} پیام به عنوان خوانده‌شده علامت‌گذاری شد."
        )

    @admin.action(
        description="علامت‌گذاری پیام‌های انتخاب‌شده به عنوان خوانده‌نشده"
    )
    def mark_as_unseen(self, request, queryset):

        updated = queryset.update(
            seen=False
        )

        self.message_user(
            request,
            f"{updated} پیام به عنوان خوانده‌نشده علامت‌گذاری شد."
        )