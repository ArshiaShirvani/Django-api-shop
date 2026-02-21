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
from django.db.models import F, Min, Q, ExpressionWrapper, IntegerField, OuterRef, Subquery, Exists
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
    page_size = 18
    page_size_query_param = "page_size"
    max_page_size = 50



class ProductListApiView(APIView):
    def get(self, request):

        products = Product.objects.filter(
            status=ProductStatus.PUBLISHED
        )

        
        color_title = request.GET.get("color")
        if color_title:
            color_variant = ProductVariant.objects.filter(
                product=OuterRef("pk"),
                is_active=True,
                stock__gt=0,
                color__title=color_title
            )
            products = products.annotate(
                has_color=Exists(color_variant)
            ).filter(has_color=True)

        
        size = request.GET.get("size")
        if size:
            size_variant = ProductVariant.objects.filter(
                product=OuterRef("pk"),
                is_active=True,
                stock__gt=0,
                size__title=size
            )
            products = products.annotate(
                has_size=Exists(size_variant)
            ).filter(has_size=True)

        
        category_slug = request.GET.get("category")
        if category_slug:
            products = products.filter(categories__slug=category_slug)

        
        variant_price_qs = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
            stock__gt=0
        ).annotate(
            final_price=F("price") * (100 - F("discount_percent")) / 100
        )

        
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        price_filter_qs = variant_price_qs

        if min_price:
            price_filter_qs = price_filter_qs.filter(final_price__gte=min_price)

        if max_price:
            price_filter_qs = price_filter_qs.filter(final_price__lte=max_price)

        if min_price or max_price:
            products = products.annotate(
                has_price=Exists(price_filter_qs)
            ).filter(has_price=True)

        
        price_subquery = variant_price_qs.values("final_price").order_by("final_price")[:1]

        products = products.annotate(
            display_price=Subquery(price_subquery, output_field=IntegerField())
        )

        
        ordering = request.GET.get("ordering")

        if ordering == "newest":
            products = products.order_by("-id")

        elif ordering == "oldest":
            products = products.order_by("id")

        elif ordering == "price_desc":
            products = products.order_by("-display_price")

        elif ordering == "price_asc":
            products = products.order_by("display_price")

        else:
            products = products.order_by("-id")

        
        products = products.prefetch_related(
            "images",
            "categories",
            "variants__size",
            "variants__color"
        )

        
        paginator = ProductPagination()
        page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        
        sizes = ProductSize.objects.all().values("id", "title")
        categories = ProductCategory.objects.all().values("id", "title", "slug")
        colors = ProductVariant.objects.filter(
            is_active=True,
            stock__gt=0
        ).values(
            "color__id",
            "color__title",
            "color__code"
        ).distinct()

        response = paginator.get_paginated_response(serializer.data)
        response.data["categories"] = list(categories)
        response.data["colors"] = list(colors)
        response.data["sizes"] = list(sizes)

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
