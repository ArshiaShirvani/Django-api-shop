from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory
)

from .serializers import (
    WebsiteSettingSerializer,
    HomeBannerSerializer,
    SecondaryBannerSerializer,
    HomeCategorySerializer
)


from shop.models import (
    Product,
    ProductStatus
)

from shop.seralizers import ProductListSerializer

from django.db.models import (
    OuterRef,
    Subquery,
    IntegerField
)
from django.db.models import Max
from shop.models import ProductVariant


class HomeAPIView(APIView):


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
        ).order_by(
            "id"
        )


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

        discount_products = Product.objects.filter(
            status=ProductStatus.PUBLISHED,
            variants__is_active=True,
            variants__stock__gt=0,
            variants__discount_percent__gt=0
        ).annotate(
            best_variant_discount=Max(
                "variants__discount_percent"
            )
        ).order_by(
            "-best_variant_discount"
        ).distinct()[:4]
        
        discount_products_data = ProductListSerializer(
            discount_products,
            many=True,
            context={
                "request": request
            }
        ).data




        return Response({

            "settings": setting_data,

            "banners": banners_data,

            "secondary_banner": secondary_data,

            "categories": categories_data,

            "discount_products": discount_products_data

        })