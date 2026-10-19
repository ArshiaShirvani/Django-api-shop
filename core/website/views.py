from django.db.models import (
    OuterRef,
    Subquery,
    IntegerField,
    F,
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from admin_panel.permissions import IsAdminPanelUser

from .models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory,
    ContactMessage,
    WebsiteStatus,
    
)

from .serializers import (
    WebsiteSettingSerializer,
    HomeBannerSerializer,
    SecondaryBannerSerializer,
    HomeCategorySerializer,
    ContactMessageSerializer,
    AdminWebsiteStatusSerializer
)

from shop.models import (
    Product,
    ProductStatus,
    ProductVariant
)

from shop.seralizers import ProductListSerializer
from shop.views import ProductBaseMixin


class HomeAPIView(ProductBaseMixin, APIView):

    def get(self, request):

        # =========================
        # Website Settings
        # =========================

        setting = WebsiteSetting.objects.first()

        setting_data = None

        if setting:
            setting_data = WebsiteSettingSerializer(
                setting,
                context={
                    "request": request
                }
            ).data

        # =========================
        # Main Banners
        # =========================

        banners = HomeBanner.objects.filter(
            is_active=True
        ).order_by("id")

        banners_data = HomeBannerSerializer(
            banners,
            many=True,
            context={
                "request": request
            }
        ).data

        # =========================
        # Secondary Banner
        # =========================

        secondary_banner = SecondaryBanner.objects.filter(
            is_active=True
        ).first()

        secondary_data = None

        if secondary_banner:
            secondary_data = SecondaryBannerSerializer(
                secondary_banner,
                context={
                    "request": request
                }
            ).data

        # =========================
        # Home Categories
        # =========================

        categories = HomeCategory.objects.filter(
            is_active=True
        ).select_related(
            "category"
        )

        categories_data = HomeCategorySerializer(
            categories,
            many=True,
            context={
                "request": request
            }
        ).data

        # =========================
        # Discount Products
        # =========================

        discount_products = (
            self.get_queryset()
            .filter(
                best_variant_discount__gt=0
            )
            .order_by(
                "-best_variant_discount"
            )[:4]
        )

        discount_products_data = ProductListSerializer(
            discount_products,
            many=True,
            context={
                "request": request
            }
        ).data

        # =========================
        # Response
        # =========================

        return Response({

            "settings": setting_data,

            "banners": banners_data,

            "secondary_banner": secondary_data,

            "categories": categories_data,

            "discount_products": discount_products_data

        })
        
# ==========================================
# CONTACT MESSAGE API
# ==========================================

class ContactMessageAPIView(APIView):

    def post(self, request):

        serializer = ContactMessageSerializer(
            data=request.data
        )

        if serializer.is_valid():

            contact_message = serializer.save()

            return Response(
                {
                    "message": "پیام شما با موفقیت ارسال شد.",
                    "data": ContactMessageSerializer(
                        contact_message
                    ).data
                },
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )
        
class AdminWebsiteStatusAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="دریافت وضعیت سایت",
        description=(
            "وضعیت فعلی سایت را نمایش می‌دهد."
        ),
        responses={
            200: AdminWebsiteStatusSerializer,
            404: OpenApiResponse(
                description="وضعیت سایت پیدا نشد."
            ),
        },
    )
    def get(self, request):

        website_status = WebsiteStatus.objects.first()

        if not website_status:
            return Response(
                {
                    "success": False,
                    "message": "وضعیت سایت تنظیم نشده است.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminWebsiteStatusSerializer(
            website_status
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Admin Panel - Website"],
        summary="تغییر وضعیت سایت",
        description=(
            "وضعیت سایت را به یکی از حالت‌های "
            "در حال اجرا، در حال تعمیر یا متوقف شده تغییر می‌دهد."
        ),
        request=AdminWebsiteStatusSerializer,
        responses={
            200: AdminWebsiteStatusSerializer,
            400: OpenApiResponse(
                description="وضعیت ارسال‌شده نامعتبر است."
            ),
            404: OpenApiResponse(
                description="وضعیت سایت پیدا نشد."
            ),
        },
    )
    def patch(self, request):

        website_status = WebsiteStatus.objects.first()

        if not website_status:
            return Response(
                {
                    "success": False,
                    "message": "وضعیت سایت تنظیم نشده است.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminWebsiteStatusSerializer(
            website_status,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )