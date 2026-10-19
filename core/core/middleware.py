from django.http import JsonResponse

from website.models import WebsiteStatus


class WebsiteStatusMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # =====================================================
        # مسیرهایی که نباید تحت تأثیر وضعیت سایت باشند
        # =====================================================

        excluded_paths = (
            "/admin-panel/",
            "/admin/",
            "/swagger/",
            "/redoc/",
            "/schema/",
        )

        if request.path.startswith(excluded_paths):
            return self.get_response(request)

        # =====================================================
        # دریافت وضعیت فعلی سایت
        # =====================================================

        website_status = WebsiteStatus.objects.first()

        # اگر هنوز وضعیت سایت ایجاد نشده باشد،
        # سایت را در حالت عادی در نظر می‌گیریم.
        if not website_status:
            return self.get_response(request)

        # =====================================================
        # سایت در حال اجرا
        # =====================================================

        if website_status.status == WebsiteStatus.Status.RUNNING:
            return self.get_response(request)

        # =====================================================
        # سایت در حال تعمیر
        # =====================================================

        if website_status.status == WebsiteStatus.Status.MAINTENANCE:
            return JsonResponse(
                {
                    "success": False,
                    "status": "maintenance",
                    "message": "سایت در حال تعمیر و بروزرسانی است.",
                },
                status=503,
            )

        # =====================================================
        # سایت متوقف شده
        # =====================================================

        if website_status.status == WebsiteStatus.Status.STOPPED:
            return JsonResponse(
                {
                    "success": False,
                    "status": "stopped",
                    "message": "سایت در حال حاضر متوقف است.",
                },
                status=503,
            )

        # =====================================================
        # حالت پیش‌فرض
        # =====================================================

        return self.get_response(request)