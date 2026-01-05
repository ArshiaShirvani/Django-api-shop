from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Profile,OTP


# =========================
# Profile Inline Admin
# =========================
class ProfileInline(admin.StackedInline):
    """
    Inline profile display inside the user admin panel
    """
    model = Profile
    can_delete = False
    verbose_name = "Profile"
    verbose_name_plural = "Profile"
    fk_name = "user"
    extra = 0
    fields = ("first_name", "last_name")
    readonly_fields = ()


# =========================
# Custom User Admin
# =========================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Advanced admin configuration for custom User model
    """

    ordering = ("-created_date",)

    list_display = (
        "phone_number",
        "role",
        "is_verified",
        "is_staff",
        "is_active",
        "created_date",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
        "is_verified",
        "created_date",
    )

    search_fields = (
        "phone_number",
        "profile__first_name",
        "profile__last_name",
    )

    readonly_fields = (
        "created_date",
        "updated_date",
        "last_login",
    )

    fieldsets = (
        (_("Main Information"), {
            "fields": (
                "phone_number",
                "password",
                "role",
            )
        }),
        (_("Account Status"), {
            "fields": (
                "is_active",
                "is_verified",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("System Information"), {
            "fields": (
                "last_login",
                "created_date",
                "updated_date",
            )
        }),
    )

    add_fieldsets = (
        (_("Create New User"), {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "password1",
                "password2",
                "role",
                "is_active",
                "is_verified",
            ),
        }),
    )

    inlines = (ProfileInline,)

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    list_per_page = 25
    save_on_top = True
    autocomplete_fields = ("groups",)

    def get_queryset(self, request):
        """
        Optimize queryset to prevent N+1 query problem
        """
        qs = super().get_queryset(request)
        return qs.select_related("profile")

    def get_fullname(self, obj):
        """
        Return user's full name from related profile
        """
        return obj.profile.get_fullname() if hasattr(obj, "profile") else "-"
    get_fullname.short_description = "Full Name"


# =========================
# Profile Admin
# =========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile model
    """

    list_display = (
        "get_phone_number",
        "first_name",
        "last_name",
        "created_date",
    )

    list_filter = (
        "created_date",
    )

    search_fields = (
        "user__phone_number",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "created_date",
        "updated_date",
    )

    fieldsets = (
        ("User Information", {
            "fields": (
                "user",
            )
        }),
        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
            )
        }),
        ("System Information", {
            "fields": (
                "created_date",
                "updated_date",
            )
        }),
    )

    autocomplete_fields = ("user",)
    list_per_page = 25
    save_on_top = True

    def get_phone_number(self, obj):
        """
        Display user's phone number
        """
        return obj.user.phone_number
    get_phone_number.short_description = "Phone Number"


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """
    Admin configuration for OTP model
    Used mainly for monitoring and debugging
    """

    ordering = ("-created_date",)

    list_display = (
        "phone_number",
        "code",
        "is_used",
        "attempts",
        "expires_date",
        "created_date",
    )

    list_filter = (
        "is_used",
        "created_date",
        "expires_date",
    )

    search_fields = (
        "phone_number",
        "code",
    )

    readonly_fields = (
        "phone_number",
        "code",
        "is_used",
        "attempts",
        "expires_date",
        "created_date",
    )

    fieldsets = (
        ("OTP Information", {
            "fields": (
                "phone_number",
                "code",
            )
        }),
        ("Status", {
            "fields": (
                "is_used",
                "attempts",
                "expires_date",
            )
        }),
        ("System Information", {
            "fields": (
                "created_date",
            )
        }),
    )

    list_per_page = 25
