from django.contrib import admin
from .models import PaymentModel, PaymentStatusType
from django.utils.html import format_html


@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):

    
    list_display = (
        "id",
        "authority_id",
        "ref_id",
        "amount",
        "status_colored",
        "response_code",
        "created_date",
    )

    list_filter = (
        "status",
        "created_date",
    )

    search_fields = (
        "authority_id",
        "ref_id",
    )

    ordering = ("-created_date",)

    
    readonly_fields = (
        "authority_id",
        "ref_id",
        "amount",
        "status",
        "response_code",
        "response_json",
        "created_date",
        "updated_date",
    )

    
    fieldsets = (
        ("اطلاعات پرداخت", {
            "fields": (
                "authority_id",
                "ref_id",
                "amount",
                "status",
                "response_code",
            )
        }),
        ("جزئیات پاسخ درگاه", {
            "fields": ("response_json",),
            "classes": ("collapse",)
        }),
        ("اطلاعات زمانی", {
            "fields": ("created_date", "updated_date")
        }),
    )

    
    def status_colored(self, obj):
        color_map = {
            PaymentStatusType.PENDING: "#f39c12",
            PaymentStatusType.SUCCESS: "#27ae60",
            PaymentStatusType.FAILED: "#e74c3c",
        }
        label_map = {
            PaymentStatusType.PENDING: "در انتظار",
            PaymentStatusType.SUCCESS: "موفق",
            PaymentStatusType.FAILED: "ناموفق",
        }
        color = color_map.get(obj.status, "black")
        label = label_map.get(obj.status, "نامشخص")
        return format_html(f'<b style="color:{color}">{label}</b>')

    status_colored.short_description = "وضعیت"

    
    def has_change_permission(self, request, obj=None):
        if obj and obj.status == PaymentStatusType.SUCCESS:
            return False
        return super().has_change_permission(request, obj)

    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == PaymentStatusType.SUCCESS:
            return False
        return super().has_delete_permission(request, obj)