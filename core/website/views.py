from django.db.models import (
    OuterRef,
    Subquery,
    IntegerField,
    F,
)

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory,
    ContactMessage,
)

from .serializers import (
    WebsiteSettingSerializer,
    HomeBannerSerializer,
    SecondaryBannerSerializer,
    HomeCategorySerializer,
    ContactMessageSerializer
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