from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .models import (
    Product,
    ProductCategory,
    ProductSize,
    ProductColor,
    ProductVariant,
    ProductImages,
    ProductStatus
)
from .seralizers import (
    ProductCategorySerilizer,
    ProductColorSerilizer,
    ProductSizeSerilizer,
    ProductListSerializer,
    ProductImageSerilizer,
    ProductVariantSerilizer,
    ProductDetailSerializer
)
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Min, F,Q,ExpressionWrapper, IntegerField
from django.db.models import Prefetch
from .pagination import ProductPagination
from rest_framework.pagination import PageNumberPagination


class TestApiView(APIView):

    def get(self, request):
        return Response(
            {"message": "Api work correct"},
            status=status.HTTP_200_OK
        )
        
        


class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 50

class ProductListApiView(APIView):
    def get(self, request):

        final_price_expr = ExpressionWrapper(
            F("variants__price") * (100 - F("variants__discount_percent")) / 100,
            output_field=IntegerField()
        )

        # 🔹 فیلترها قبل از prefetch
        filters = Q(status=ProductStatus.PUBLISHED)
        category_slug = request.GET.get("category")
        if category_slug:
            filters &= Q(categories__slug=category_slug)

        size = request.GET.get("size")
        if size:
            filters &= Q(variants__size__title=size)

        color = request.GET.get("color")
        if color:
            filters &= Q(variants__color__code=color)

        products = Product.objects.filter(filters).annotate(
            display_price=Min(final_price_expr)
        ).distinct().prefetch_related(
            "images",
            "categories",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True, stock__gt=0).select_related("size", "color")
            )
        ).order_by("-id")

        paginator = ProductPagination()
        page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(page, many=True, context={"request": request})

        categories = ProductCategory.objects.all().values("id", "title", "slug")
        colors = ProductVariant.objects.filter(is_active=True, stock__gt=0).values(
            "color__id", "color__title", "color__code"
        ).distinct()

        response = paginator.get_paginated_response(serializer.data)
        response.data["categories"] = list(categories)
        response.data["colors"] = list(colors)

        return response




    
    
    
class ProductDetailApiView(APIView):

    def get(self, request, slug):

        product = get_object_or_404(
            Product.objects.filter(
                status=ProductStatus.PUBLISHED
            ).prefetch_related(
                "images",
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True,
                        stock__gt=0
                    ).select_related("size", "color")
                )
            ),
            slug=slug
        )

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
