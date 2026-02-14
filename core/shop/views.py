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
from django.db.models import Min, F, ExpressionWrapper, IntegerField
from django.db.models import Prefetch


class TestApiView(APIView):

    def get(self, request):
        return Response(
            {"message": "Api work correct"},
            status=status.HTTP_200_OK
        )
        
        
class ProductListApiView(APIView):

    def get(self, request):

        final_price_expr = ExpressionWrapper(
            F("variants__price") * (100 - F("variants__discount_percent")) / 100,
            output_field=IntegerField()
        )

        products = Product.objects.filter(
            status=ProductStatus.PUBLISHED
        ).prefetch_related(
            'images',
            'categories',
            Prefetch(
                'variants',
                queryset=ProductVariant.objects.filter(
                    is_active=True,
                    stock__gt=0
                ).select_related('size', 'color')
            )
        ).annotate(
            display_price=Min(final_price_expr)
        ).distinct()

        
        category_slug = request.GET.get("category")
        if category_slug:
            products = products.filter(categories__slug=category_slug)

        size = request.GET.get("size")
        if size:
            products = products.filter(variants__size__title=size)

        color = request.GET.get("color")
        if color:
            products = products.filter(variants__color__title=color)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
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
