from django.core.exceptions import ValidationError

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from rest_framework import status
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from website.models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory,
)

from admin_panel.permissions import IsAdminPanelUser

from admin_panel.serializers.website import (
    AdminWebsiteSettingSerializer,
    AdminHomeBannerSerializer,
    AdminSecondaryBannerSerializer,
    AdminHomeCategorySerializer,
)


# ==========================================================
# COMMON
# ==========================================================

class AdminWebsiteBaseView(APIView):

    permission_classes = (
        IsAuthenticated,
        IsAdminPanelUser,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
        JSONParser,
    )

    @staticmethod
    def validation_error_response(exc):

        if hasattr(exc, "message_dict"):
            detail = exc.message_dict
        else:
            detail = exc.messages

        return Response(
            {
                "detail": detail
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# WEBSITE SETTING
# ==========================================================

class AdminWebsiteSettingView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="دریافت تنظیمات سایت",
        description="دریافت تنها رکورد تنظیمات اصلی سایت.",
        responses={
            200: AdminWebsiteSettingSerializer,
            404: OpenApiResponse(
                description="تنظیمات سایت هنوز ایجاد نشده است."
            ),
        },
    )
    def get(self, request):

        setting = WebsiteSetting.objects.first()

        if not setting:
            return Response(
                {
                    "detail": "تنظیمات سایت هنوز ایجاد نشده است."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminWebsiteSettingSerializer(
            setting,
            context={"request": request},
        )

        return Response(serializer.data)

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ایجاد تنظیمات سایت",
        description=(
            "ایجاد تنظیمات سایت. "
            "فقط یک رکورد WebsiteSetting مجاز است."
        ),
        request=AdminWebsiteSettingSerializer,
        responses={
            201: AdminWebsiteSettingSerializer,
            400: OpenApiResponse(
                description="تنظیمات سایت قبلاً ایجاد شده است."
            ),
        },
    )
    def post(self, request):

        if WebsiteSetting.objects.exists():
            return Response(
                {
                    "detail": "تنظیمات سایت قبلاً ایجاد شده است."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdminWebsiteSettingSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        setting = serializer.save()

        return Response(
            AdminWebsiteSettingSerializer(
                setting,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش کامل تنظیمات سایت",
        description="ویرایش کامل اطلاعات تنظیمات سایت.",
        request=AdminWebsiteSettingSerializer,
        responses={
            200: AdminWebsiteSettingSerializer,
            404: OpenApiResponse(
                description="تنظیمات سایت پیدا نشد."
            ),
        },
    )
    def put(self, request):

        setting = WebsiteSetting.objects.first()

        if not setting:
            return Response(
                {
                    "detail": "تنظیمات سایت هنوز ایجاد نشده است."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminWebsiteSettingSerializer(
            setting,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        setting = serializer.save()

        return Response(
            AdminWebsiteSettingSerializer(
                setting,
                context={"request": request},
            ).data
        )

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش بخشی از تنظیمات سایت",
        description="ویرایش بخشی از اطلاعات تنظیمات سایت.",
        request=AdminWebsiteSettingSerializer,
        responses={
            200: AdminWebsiteSettingSerializer,
            404: OpenApiResponse(
                description="تنظیمات سایت پیدا نشد."
            ),
        },
    )
    def patch(self, request):

        setting = WebsiteSetting.objects.first()

        if not setting:
            return Response(
                {
                    "detail": "تنظیمات سایت هنوز ایجاد نشده است."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminWebsiteSettingSerializer(
            setting,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        setting = serializer.save()

        return Response(
            AdminWebsiteSettingSerializer(
                setting,
                context={"request": request},
            ).data
        )


# ==========================================================
# HOME BANNER - LIST
# ==========================================================

class AdminHomeBannerListView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="لیست بنرهای صفحه اصلی",
        description="دریافت لیست بنرهای اصلی صفحه اصلی.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="جستجو بر اساس عنوان بنر",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_active",
                description="فیلتر فعال/غیرفعال",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="is_first",
                description="فیلتر بنر اول",
                required=False,
                type=bool,
            ),
        ],
        responses=AdminHomeBannerSerializer(many=True),
    )
    def get(self, request):

        queryset = HomeBanner.objects.all()

        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        is_active = request.query_params.get("is_active")

        if is_active is not None:

            if is_active.lower() in ("true", "1"):
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() in ("false", "0"):
                queryset = queryset.filter(is_active=False)

        is_first = request.query_params.get("is_first")

        if is_first is not None:

            if is_first.lower() in ("true", "1"):
                queryset = queryset.filter(is_first=True)

            elif is_first.lower() in ("false", "0"):
                queryset = queryset.filter(is_first=False)

        queryset = queryset.order_by(
            "order",
            "-id",
        )

        serializer = AdminHomeBannerSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================================
# HOME BANNER - CREATE
# ==========================================================

class AdminHomeBannerCreateView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ایجاد بنر صفحه اصلی",
        description=(
            "ایجاد یک بنر اصلی. "
            "تصویر اصلی و تصویر موبایل قابل ارسال هستند."
        ),
        request=AdminHomeBannerSerializer,
        responses={
            201: AdminHomeBannerSerializer,
            400: OpenApiResponse(
                description="اطلاعات ارسال‌شده معتبر نیست."
            ),
        },
    )
    def post(self, request):

        serializer = AdminHomeBannerSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            banner = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminHomeBannerSerializer(
                banner,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# HOME BANNER - DETAIL
# ==========================================================

class AdminHomeBannerDetailView(AdminWebsiteBaseView):

    def get_object(self, pk):
        return HomeBanner.objects.get(pk=pk)

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="جزئیات بنر صفحه اصلی",
        responses={
            200: AdminHomeBannerSerializer,
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        try:
            banner = self.get_object(pk)

        except HomeBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminHomeBannerSerializer(
            banner,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================================
# HOME BANNER - UPDATE
# ==========================================================

class AdminHomeBannerUpdateView(AdminWebsiteBaseView):

    def get_object(self, pk):
        return HomeBanner.objects.get(pk=pk)

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش کامل بنر",
        request=AdminHomeBannerSerializer,
        responses={
            200: AdminHomeBannerSerializer,
            400: OpenApiResponse(
                description="اطلاعات بنر معتبر نیست."
            ),
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def put(self, request, pk):

        try:
            banner = self.get_object(pk)

        except HomeBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminHomeBannerSerializer(
            banner,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            banner = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminHomeBannerSerializer(
                banner,
                context={"request": request},
            ).data
        )

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش بخشی از بنر",
        request=AdminHomeBannerSerializer,
        responses={
            200: AdminHomeBannerSerializer,
            400: OpenApiResponse(
                description="اطلاعات بنر معتبر نیست."
            ),
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def patch(self, request, pk):

        try:
            banner = self.get_object(pk)

        except HomeBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminHomeBannerSerializer(
            banner,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            banner = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminHomeBannerSerializer(
                banner,
                context={"request": request},
            ).data
        )


# ==========================================================
# HOME BANNER - DELETE
# ==========================================================

class AdminHomeBannerDeleteView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="حذف بنر صفحه اصلی",
        description="حذف یک بنر از بنرهای صفحه اصلی.",
        request=None,
        responses={
            204: OpenApiResponse(
                description="بنر با موفقیت حذف شد."
            ),
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def delete(self, request, pk):

        try:
            banner = HomeBanner.objects.get(pk=pk)

        except HomeBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        banner.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ==========================================================
# SECONDARY BANNER - LIST
# ==========================================================

class AdminSecondaryBannerListView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="دریافت بنر ثانویه",
        description="دریافت لیست بنرهای ثانویه.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="جستجو بر اساس عنوان",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_active",
                description="فیلتر فعال/غیرفعال",
                required=False,
                type=bool,
            ),
        ],
        responses=AdminSecondaryBannerSerializer(many=True),
    )
    def get(self, request):

        queryset = SecondaryBanner.objects.all()

        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        is_active = request.query_params.get("is_active")

        if is_active is not None:

            if is_active.lower() in ("true", "1"):
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() in ("false", "0"):
                queryset = queryset.filter(is_active=False)

        queryset = queryset.order_by(
            "order",
            "-id",
        )

        serializer = AdminSecondaryBannerSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================================
# SECONDARY BANNER - CREATE
# ==========================================================

class AdminSecondaryBannerCreateView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ایجاد بنر ثانویه",
        request=AdminSecondaryBannerSerializer,
        responses={
            201: AdminSecondaryBannerSerializer,
            400: OpenApiResponse(
                description="بنر ثانویه معتبر نیست."
            ),
        },
    )
    def post(self, request):

        serializer = AdminSecondaryBannerSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            banner = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminSecondaryBannerSerializer(
                banner,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# SECONDARY BANNER - DETAIL
# ==========================================================

class AdminSecondaryBannerDetailView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="جزئیات بنر ثانویه",
        responses={
            200: AdminSecondaryBannerSerializer,
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        try:
            banner = SecondaryBanner.objects.get(pk=pk)

        except SecondaryBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر ثانویه موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminSecondaryBannerSerializer(
            banner,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================================
# SECONDARY BANNER - UPDATE
# ==========================================================

class AdminSecondaryBannerUpdateView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش بنر ثانویه",
        request=AdminSecondaryBannerSerializer,
        responses={
            200: AdminSecondaryBannerSerializer,
            400: OpenApiResponse(
                description="اطلاعات بنر معتبر نیست."
            ),
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def put(self, request, pk):

        try:
            banner = SecondaryBanner.objects.get(pk=pk)

        except SecondaryBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر ثانویه موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminSecondaryBannerSerializer(
            banner,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            banner = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminSecondaryBannerSerializer(
                banner,
                context={"request": request},
            ).data
        )

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش بخشی از بنر ثانویه",
        request=AdminSecondaryBannerSerializer,
        responses={
            200: AdminSecondaryBannerSerializer,
            400: OpenApiResponse(
                description="اطلاعات بنر معتبر نیست."
            ),
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def patch(self, request, pk):

        try:
            banner = SecondaryBanner.objects.get(pk=pk)

        except SecondaryBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر ثانویه موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminSecondaryBannerSerializer(
            banner,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            banner = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminSecondaryBannerSerializer(
                banner,
                context={"request": request},
            ).data
        )


# ==========================================================
# SECONDARY BANNER - DELETE
# ==========================================================

class AdminSecondaryBannerDeleteView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="حذف بنر ثانویه",
        description="حذف بنر ثانویه سایت.",
        request=None,
        responses={
            204: OpenApiResponse(
                description="بنر ثانویه با موفقیت حذف شد."
            ),
            404: OpenApiResponse(
                description="بنر پیدا نشد."
            ),
        },
    )
    def delete(self, request, pk):

        try:
            banner = SecondaryBanner.objects.get(pk=pk)

        except SecondaryBanner.DoesNotExist:
            return Response(
                {
                    "detail": "بنر ثانویه موردنظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        banner.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ==========================================================
# HOME CATEGORY - LIST
# ==========================================================

class AdminHomeCategoryListView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="لیست دسته‌بندی‌های صفحه اصلی",
        description=(
            "دریافت دسته‌بندی‌هایی که برای صفحه اصلی "
            "در نظر گرفته شده‌اند."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                description=(
                    "جستجو بر اساس عنوان دسته‌بندی "
                    "یا عنوان نمایشی"
                ),
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_active",
                description="فیلتر فعال/غیرفعال",
                required=False,
                type=bool,
            ),
        ],
        responses=AdminHomeCategorySerializer(many=True),
    )
    def get(self, request):

        queryset = (
            HomeCategory.objects
            .select_related("category")
            .all()
        )

        search = request.query_params.get("search")

        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(category__title__icontains=search)
                |
                Q(custom_title__icontains=search)
            )

        is_active = request.query_params.get("is_active")

        if is_active is not None:

            if is_active.lower() in ("true", "1"):
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() in ("false", "0"):
                queryset = queryset.filter(is_active=False)

        queryset = queryset.order_by("-id")

        serializer = AdminHomeCategorySerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================================
# HOME CATEGORY - CREATE
# ==========================================================

class AdminHomeCategoryCreateView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ایجاد دسته‌بندی صفحه اصلی",
        request=AdminHomeCategorySerializer,
        responses={
            201: AdminHomeCategorySerializer,
            400: OpenApiResponse(
                description="اطلاعات دسته‌بندی معتبر نیست."
            ),
        },
    )
    def post(self, request):

        serializer = AdminHomeCategorySerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            category = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminHomeCategorySerializer(
                category,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# HOME CATEGORY - DETAIL
# ==========================================================

class AdminHomeCategoryDetailView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="جزئیات دسته‌بندی صفحه اصلی",
        responses={
            200: AdminHomeCategorySerializer,
            404: OpenApiResponse(
                description="دسته‌بندی پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        try:
            category = (
                HomeCategory.objects
                .select_related("category")
                .get(pk=pk)
            )

        except HomeCategory.DoesNotExist:
            return Response(
                {
                    "detail": "دسته‌بندی صفحه اصلی پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminHomeCategorySerializer(
            category,
            context={"request": request},
        )

        return Response(serializer.data)


# ==========================================================
# HOME CATEGORY - UPDATE
# ==========================================================

class AdminHomeCategoryUpdateView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش دسته‌بندی صفحه اصلی",
        request=AdminHomeCategorySerializer,
        responses={
            200: AdminHomeCategorySerializer,
            400: OpenApiResponse(
                description="اطلاعات معتبر نیست."
            ),
            404: OpenApiResponse(
                description="دسته‌بندی پیدا نشد."
            ),
        },
    )
    def put(self, request, pk):

        try:
            category = HomeCategory.objects.get(pk=pk)

        except HomeCategory.DoesNotExist:
            return Response(
                {
                    "detail": "دسته‌بندی صفحه اصلی پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminHomeCategorySerializer(
            category,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            category = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminHomeCategorySerializer(
                category,
                context={"request": request},
            ).data
        )

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="ویرایش بخشی از دسته‌بندی",
        request=AdminHomeCategorySerializer,
        responses={
            200: AdminHomeCategorySerializer,
            400: OpenApiResponse(
                description="اطلاعات معتبر نیست."
            ),
            404: OpenApiResponse(
                description="دسته‌بندی پیدا نشد."
            ),
        },
    )
    def patch(self, request, pk):

        try:
            category = HomeCategory.objects.get(pk=pk)

        except HomeCategory.DoesNotExist:
            return Response(
                {
                    "detail": "دسته‌بندی صفحه اصلی پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminHomeCategorySerializer(
            category,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            category = serializer.save()

        except ValidationError as exc:
            return self.validation_error_response(exc)

        return Response(
            AdminHomeCategorySerializer(
                category,
                context={"request": request},
            ).data
        )


# ==========================================================
# HOME CATEGORY - DELETE
# ==========================================================

class AdminHomeCategoryDeleteView(AdminWebsiteBaseView):

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="حذف دسته‌بندی صفحه اصلی",
        description="حذف یک دسته‌بندی از صفحه اصلی.",
        request=None,
        responses={
            204: OpenApiResponse(
                description="دسته‌بندی با موفقیت حذف شد."
            ),
            404: OpenApiResponse(
                description="دسته‌بندی پیدا نشد."
            ),
        },
    )
    def delete(self, request, pk):

        try:
            category = HomeCategory.objects.get(pk=pk)

        except HomeCategory.DoesNotExist:
            return Response(
                {
                    "detail": "دسته‌بندی صفحه اصلی پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        category.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

