from django.shortcuts import get_object_or_404
from django.db.models import (
    Exists,
    OuterRef,
    Prefetch,
    IntegerField,
    F,
    Subquery,
    Q,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    Product,
    ProductCategory,
    ProductVariant,
    ProductImages,
    ProductSize,
    ProductStatus,
    FeatureValue,
    SizeGuide,
)
from review.models import Review
from .seralizers import (
    ProductListSerializer,
    ProductDetailSerializer,
)



# ==========================================
# Pagination
# ==========================================

class ProductPagination(PageNumberPagination):

    page_size = 18

    page_size_query_param = "page_size"

    max_page_size = 60


# ==========================================
# Base Query
# ==========================================

class ProductBaseMixin:

    def get_queryset(self):

        best_variant = ProductVariant.objects.filter(
            product=OuterRef("pk"),
            is_active=True,
            stock__gt=0,
        ).annotate(
            final_price=(
                F("price") *
                (100 - F("discount_percent"))
            ) / 100
        ).order_by(
            "final_price"
        )

        return (
            Product.objects.filter(
                status=ProductStatus.PUBLISHED
            )
            .annotate(

                best_variant_price=Subquery(
                    best_variant.values(
                        "final_price"
                    )[:1],
                    output_field=IntegerField()
                ),

                best_variant_original_price=Subquery(
                    best_variant.values(
                        "price"
                    )[:1]
                ),

                best_variant_discount=Subquery(
                    best_variant.values(
                        "discount_percent"
                    )[:1]
                )

            )
            .prefetch_related(

                "categories",

                

            )
        )

class ProductListApiView(ProductBaseMixin, APIView):

    pagination_class = ProductPagination

    def get_category_children(self, category):

        ids = [category.id]

        children = list(
            category.children.all()
        )

        for child in children:

            ids.extend(
                self.get_category_children(
                    child
                )
            )

        return ids

    def get(self, request):

        products = self.get_queryset()

        # ---------------------------------
        # Category
        # ---------------------------------

        category_slug = request.GET.get("category")

        if category_slug:

            category = get_object_or_404(
                ProductCategory,
                slug=category_slug
            )

            ids = self.get_category_children(
                category
            )

            products = products.filter(
                categories__id__in=ids
            ).distinct()

        # ---------------------------------
        # Search
        # ---------------------------------

        search = request.GET.get("search")

        if search:

            products = products.filter(

                Q(title__icontains=search)

                |

                Q(
                    brief_description__icontains=search
                )

            )

        # ---------------------------------
        # Color
        # ---------------------------------

        colors = request.GET.getlist("color")

        if colors:

            products = products.filter(

                variants__color__code__in=colors,

                variants__is_active=True,

                variants__stock__gt=0

            ).distinct()

        # ---------------------------------
        # Size
        # ---------------------------------

        sizes = request.GET.getlist("size")

        if sizes:

            products = products.filter(

                variants__size__title__in=sizes,

                variants__is_active=True,

                variants__stock__gt=0

            ).distinct()
            
         # ---------------------------------
        # Price
        # ---------------------------------

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        try:
            if min_price:
                min_price = int(min_price)

                products = products.filter(
                    best_variant_price__gte=min_price
                )

            if max_price:
                max_price = int(max_price)

                products = products.filter(
                    best_variant_price__lte=max_price
                )

        except (TypeError, ValueError):
            pass

        # ---------------------------------
        # Sort
        # ---------------------------------

        ordering = request.GET.get(
            "sort",
            "newest"
        )

        ordering_map = {

            "newest": "-created_date",

            "oldest": "created_date",

            "price_asc": "best_variant_price",

            "price_desc": "-best_variant_price",

            "discount": "-best_variant_discount",

        }

        products = products.order_by(

            ordering_map.get(
                ordering,
                "-created_date"
            )

        )

        # ---------------------------------
        # Pagination
        # ---------------------------------

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(
            products,
            request
        )

        serializer = ProductListSerializer(

            page,

            many=True,

            context={
                "request": request
            }

        )

        # ---------------------------------
        # Filters
        # ---------------------------------

        categories = ProductCategory.objects.values(

            "id",

            "title",

            "slug"

        )

        sizes = ProductSize.objects.values(

            "id",

            "title"

        )

        colors = ProductVariant.objects.filter(

            is_active=True,

            stock__gt=0

        ).values(

            "color__id",

            "color__title",

            "color__code"

        ).distinct()

        response = paginator.get_paginated_response(
            serializer.data
        )

        response.data["filters"] = {

            "categories": list(categories),

            "sizes": list(sizes),

            "colors": list(colors),

        }

        return response

class ProductDetailApiView(ProductBaseMixin, APIView):

    def get(self, request, slug):


        # ---------------------------------
        # Product Query
        # ---------------------------------

        product = get_object_or_404(

            self.get_queryset()

            .prefetch_related(

                "categories",

                Prefetch(
                    "images",
                    queryset=ProductImages.objects.order_by(
                        "-is_main"
                    )
                ),


                Prefetch(
                    "variants",

                    queryset=ProductVariant.objects.filter(

                        is_active=True,

                        stock__gt=0

                    )
                    .select_related(

                        "size",

                        "color"

                    )

                ),


                Prefetch(

                    "feature_values",

                    queryset=FeatureValue.objects.select_related(

                        "feature"

                    )

                ),
                Prefetch(
                    "reviews",
                    queryset=Review.objects.select_related(
                        "user"
                    ).order_by(
                        "-created_date"
                    )
                ),
                Prefetch(
                    "size_guides",
                    queryset=SizeGuide.objects.all()
                ),

            ),

            slug=slug

        )


        # ---------------------------------
        # Similar Products
        # ---------------------------------

        category_ids = product.categories.values_list(

            "id",

            flat=True

        )


        similar_products = (

            self.get_queryset()

            .filter(

                categories__in=category_ids

            )

            .exclude(

                id=product.id

            )

            .distinct()

            [:8]

        )


        similar_serializer = ProductListSerializer(

            similar_products,

            many=True,

            context={

                "request":request

            }

        )


        serializer = ProductDetailSerializer(

            product,

            context={

                "request":request

            }

        )


        return Response({

            "product": serializer.data,

            "similar_products": similar_serializer.data

        })