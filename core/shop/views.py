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
    ProductSerilizer,
    ProductImageSerilizer,
    ProductVariantSerilizer,
)
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Prefetch, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status




class TestApiView(APIView):

    def get(self, request):
        return Response(
            {"message": "Api work correct"},
            status=status.HTTP_200_OK
        )
        
        
class ProductListApiView(APIView):

    def get(self, request):

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
        ).distinct()

        # filtering based on category
        category_slug = request.GET.get("category")
        if category_slug:
            products = products.filter(
                categories__slug=category_slug
            )

        # filtering based on size
        size = request.GET.get("size")
        if size:
            products = products.filter(
                variants__size__title=size
            )

        # filtering based on color
        color = request.GET.get("color")
        if color:
            products = products.filter(
                variants__color__title=color
            )

        # filtering based on price range
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        if min_price or max_price:

            final_price_expr = ExpressionWrapper(
                F("variants__price") * (100 - F("variants__discount_percent")) / 100,
                output_field=IntegerField()
            )

            if min_price:
                products = products.filter(final_price_expr__gte=int(min_price))

            if max_price:
                products = products.filter(final_price_expr__lte=int(max_price))

        serializer = ProductSerilizer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ProductDetailApiView(APIView):

    def get(self, request, slug):

        product = get_object_or_404(
            Product.objects.filter(
                status=ProductStatus.PUBLISHED
            ).prefetch_related(
                "categories",
                "images",
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True
                    ).select_related("size", "color")
                )
            ),
            slug=slug
        )

        serializer = ProductSerilizer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)