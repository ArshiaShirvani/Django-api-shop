from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from django.db.models import (
    F, OuterRef, Subquery, Exists,
    IntegerField, Prefetch, Q
)

from rest_framework.pagination import PageNumberPagination

from .models import (
    Product,
    ProductCategory,
    ProductSize,
    ProductVariant,
    ProductStatus
)

from .seralizers import (
    ProductListSerializer,
    ProductDetailSerializer
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

        
        best_variant_qs = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
            stock__gt=0
        ).annotate(
            final_price=F("price") * (100 - F("discount_percent")) / 100
        ).order_by("-discount_percent", "final_price")

        products = products.annotate(
            best_variant_price=Subquery(
                best_variant_qs.values("final_price")[:1],
                output_field=IntegerField()
            ),
            best_variant_original_price=Subquery(
                best_variant_qs.values("price")[:1]
            ),
            best_variant_discount=Subquery(
                best_variant_qs.values("discount_percent")[:1]
            )
        )

        
        category_slug = request.GET.get("category")
        if category_slug:
            products = products.filter(categories__slug=category_slug)

        
        color_code = request.GET.get("color")
        if color_code:
            color_variant = ProductVariant.objects.filter(
                product=OuterRef("pk"),
                is_active=True,
                stock__gt=0,
                color__code=color_code
            )
            products = products.annotate(
                has_color=Exists(color_variant)
            ).filter(has_color=True)

        
        size_title = request.GET.get("size")
        if size_title:
            size_variant = ProductVariant.objects.filter(
                product=OuterRef("pk"),
                is_active=True,
                stock__gt=0,
                size__title=size_title
            )
            products = products.annotate(
                has_size=Exists(size_variant)
            ).filter(has_size=True)

        
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        price_variant = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
            stock__gt=0
        ).annotate(
            final_price=F("price") * (100 - F("discount_percent")) / 100
        )

        if min_price:
            price_variant = price_variant.filter(final_price__gte=min_price)

        if max_price:
            price_variant = price_variant.filter(final_price__lte=max_price)

        if min_price or max_price:
            products = products.annotate(
                has_price=Exists(price_variant)
            ).filter(has_price=True)

        
        ordering = request.GET.get("sort")

        if ordering == "price_asc":
            products = products.order_by("best_variant_price")

        elif ordering == "price_desc":
            products = products.order_by("-best_variant_price")

        elif ordering == "oldest":
            products = products.order_by("created_date")

        else:  
            products = products.order_by("-created_date")

        
        products = products.prefetch_related(
            "images",
            "categories"
        )

        
        paginator = ProductPagination()
        page = paginator.paginate_queryset(products, request)

        serializer = ProductListSerializer(
            page,
            many=True,
            context={"request": request}
        )

        
        categories = ProductCategory.objects.all().values("id", "title", "slug")
        sizes = ProductSize.objects.all().values("id", "title")

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

        best_variant_qs = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
            stock__gt=0
        ).order_by("-discount_percent", "price")

        product = get_object_or_404(
            Product.objects.filter(
                status=ProductStatus.PUBLISHED
            ).annotate(
                default_variant_id=Subquery(
                    best_variant_qs.values("id")[:1]
                )
            ).prefetch_related(
                "images",
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True,
                        stock__gt=0
                    ).select_related("size", "color")
                ),
                "categories"
            ),
            slug=slug
        )

        
        product_categories = product.categories.values_list("id", flat=True)

        similar_products = Product.objects.filter(
            status=ProductStatus.PUBLISHED,
            categories__in=product_categories
        ).exclude(id=product.id).distinct()[:4]

        similar_serializer = ProductListSerializer(
            similar_products,
            many=True,
            context={"request": request}
        )

        serializer = ProductDetailSerializer(product)

        return Response({
            "product": serializer.data,
            "similar_products": similar_serializer.data
        })