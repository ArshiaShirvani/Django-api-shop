from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from shop.models import *

from order.models import OrderItem

from ..permissions import IsAdminPanelUser

from ..serializers.products import *


# ==========================================================
# PAGINATION
# ==========================================================

class AdminProductPagination(PageNumberPagination):

    page_size = 20

    page_size_query_param = "page_size"

    max_page_size = 100


# ==========================================================
# PRODUCT QUERYSET
# ==========================================================

def get_product_queryset():

    return (
        Product.objects
        .prefetch_related(
            "categories",
            "images",
            "variants__size",
            "variants__color",
            "feature_values__feature",
            "size_guides",
        )
        .annotate(
            variants_count=Count(
                "variants",
                distinct=True,
            ),
            total_stock=Sum(
                "variants__stock"
            ),
        )
    )


# ==========================================================
# PRODUCT OPTIONS
# ==========================================================

class AdminProductOptionsAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="گزینه‌های فرم ایجاد و ویرایش محصول",
        responses={200: AdminProductOptionsSerializer},
    )
    def get(self, request):
        data = {
            "categories": ProductCategory.objects.all(),
            "sizes": ProductSize.objects.all(),
            "colors": ProductColor.objects.all(),
            "features": Feature.objects.all(),
        }

        serializer = AdminProductOptionsSerializer(data)
        return Response(serializer.data)


# ==========================================================
# CREATE CATEGORY
# ==========================================================

class AdminProductCategoryCreateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ایجاد دسته‌بندی",
        request=AdminProductCategoryCreateSerializer,
        responses={201: AdminProductCategorySerializer},
    )
    def post(self, request):
        serializer = AdminProductCategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        response_serializer = AdminProductCategorySerializer(category)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# CREATE SIZE
# ==========================================================

class AdminProductSizeCreateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ایجاد سایز",
        request=AdminProductSizeCreateSerializer,
        responses={201: AdminProductSizeCreateSerializer},
    )
    def post(self, request):
        serializer = AdminProductSizeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        size = serializer.save()

        return Response(
            AdminProductSizeCreateSerializer(size).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# CREATE COLOR
# ==========================================================

class AdminProductColorCreateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ایجاد رنگ",
        request=AdminProductColorCreateSerializer,
        responses={201: AdminProductColorCreateSerializer},
    )
    def post(self, request):
        serializer = AdminProductColorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        color = serializer.save()

        return Response(
            AdminProductColorCreateSerializer(color).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# CREATE FEATURE
# ==========================================================

class AdminProductFeatureCreateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ایجاد ویژگی",
        request=AdminProductFeatureCreateSerializer,
        responses={201: AdminProductFeatureCreateSerializer},
    )
    def post(self, request):
        serializer = AdminProductFeatureCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feature = serializer.save()

        return Response(
            AdminProductFeatureCreateSerializer(feature).data,
            status=status.HTTP_201_CREATED,
        )



# ==========================================================
# PRODUCT LIST
# ==========================================================

class AdminProductListAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    pagination_class = AdminProductPagination

    @extend_schema(
        tags=["Admin - Products"],
        summary="لیست محصولات",
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                required=False,
                description="جستجو در عنوان، اسلاگ و توضیح کوتاه",
            ),
            OpenApiParameter(
                name="status",
                type=int,
                required=False,
                description="وضعیت محصول",
            ),
            OpenApiParameter(
                name="category",
                type=int,
                required=False,
                description="شناسه دسته‌بندی",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                required=False,
            ),
        ],
        responses={
            200: AdminProductListSerializer(many=True),
        },
    )
    def get(self, request):

        products = get_product_queryset()

        # ------------------------------------------
        # SEARCH
        # ------------------------------------------

        search = request.query_params.get(
            "search"
        )

        if search:

            products = products.filter(
                title__icontains=search
            )

        # ------------------------------------------
        # STATUS
        # ------------------------------------------

        product_status = request.query_params.get(
            "status"
        )

        if product_status:

            products = products.filter(
                status=product_status
            )

        # ------------------------------------------
        # CATEGORY
        # ------------------------------------------

        category = request.query_params.get(
            "category"
        )

        if category:

            products = products.filter(
                categories__id=category
            )

        # ------------------------------------------
        # PAGINATION
        # ------------------------------------------

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(
            products,
            request,
            view=self,
        )

        serializer = AdminProductListSerializer(
            page,
            many=True,
            context={
                "request": request
            },
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# ==========================================================
# PRODUCT CREATE
# ==========================================================

class AdminProductCreateAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    parser_classes = [
        JSONParser,
    ]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ایجاد محصول",
        request=AdminProductCreateSerializer,
        responses={
            201: AdminProductDetailSerializer,
        },
    )
    def post(self, request):

        serializer = AdminProductCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        with transaction.atomic():

            validated_data = serializer.validated_data

            categories = validated_data.pop(
                "categories",
                []
            )

            variants = validated_data.pop(
                "variants",
                []
            )

            feature_values = validated_data.pop(
                "feature_values",
                []
            )

            size_guides = validated_data.pop(
                "size_guides",
                []
            )

            # --------------------------------------
            # PRODUCT
            # --------------------------------------

            product = Product.objects.create(
                **validated_data
            )

            # --------------------------------------
            # CATEGORIES
            # --------------------------------------

            product.categories.set(
                categories
            )

            # --------------------------------------
            # VARIANTS
            # --------------------------------------

            ProductVariant.objects.bulk_create(
                [
                    ProductVariant(
                        product=product,
                        size=variant["size"],
                        color=variant["color"],
                        price=variant["price"],
                        discount_percent=variant.get(
                            "discount_percent",
                            0,
                        ),
                        stock=variant.get(
                            "stock",
                            0,
                        ),
                        is_active=variant.get(
                            "is_active",
                            True,
                        ),
                        sku=variant["sku"],
                    )
                    for variant in variants
                ]
            )

            # --------------------------------------
            # FEATURES
            # --------------------------------------

            FeatureValue.objects.bulk_create(
                [
                    FeatureValue(
                        product=product,
                        feature=feature["feature"],
                        value=feature["value"],
                    )
                    for feature in feature_values
                ]
            )

            # --------------------------------------
            # SIZE GUIDES
            # --------------------------------------

            SizeGuide.objects.bulk_create(
                [
                    SizeGuide(
                        product=product,
                        feature=size_guide.get(
                            "feature"
                        ),
                        value=size_guide.get(
                            "value"
                        ),
                        image=size_guide.get(
                            "image"
                        ),
                    )
                    for size_guide in size_guides
                ]
            )

        product = get_product_queryset().get(
            pk=product.pk
        )

        response_serializer = AdminProductDetailSerializer(
            product,
            context={
                "request": request
            },
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# PRODUCT DETAIL / UPDATE / DELETE
# ==========================================================

class AdminProductDetailAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    parser_classes = [
        JSONParser,
    ]

    def get_object(self, pk):

        return get_object_or_404(
            get_product_queryset(),
            pk=pk,
        )

    # ======================================================
    # GET DETAIL
    # ======================================================

    @extend_schema(
        tags=["Admin - Products"],
        summary="جزئیات محصول",
        responses={
            200: AdminProductDetailSerializer,
            404: OpenApiResponse(
                description="محصول پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        product = self.get_object(pk)

        serializer = AdminProductDetailSerializer(
            product,
            context={
                "request": request
            },
        )

        return Response(
            serializer.data
        )

    # ======================================================
    # PUT
    # ======================================================

    @extend_schema(
        tags=["Admin - Products"],
        summary="ویرایش کامل محصول",
        request=AdminProductUpdateSerializer,
        responses={
            200: AdminProductDetailSerializer,
        },
    )
    def put(self, request, pk):

        return self.update_product(
            request,
            pk,
            partial=False,
        )

    # ======================================================
    # PATCH
    # ======================================================

    @extend_schema(
        tags=["Admin - Products"],
        summary="ویرایش محصول",
        request=AdminProductUpdateSerializer,
        responses={
            200: AdminProductDetailSerializer,
        },
    )
    def patch(self, request, pk):

        return self.update_product(
            request,
            pk,
            partial=True,
        )

    # ======================================================
    # UPDATE
    # ======================================================

    def update_product(
        self,
        request,
        pk,
        partial=False,
    ):

        product = self.get_object(pk)

        serializer = AdminProductUpdateSerializer(
            product,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        with transaction.atomic():

            validated_data = serializer.validated_data

            categories = validated_data.pop(
                "categories",
                None,
            )

            variants = validated_data.pop(
                "variants",
                None,
            )

            feature_values = validated_data.pop(
                "feature_values",
                None,
            )

            size_guides = validated_data.pop(
                "size_guides",
                None,
            )

            # --------------------------------------
            # BASIC FIELDS
            # --------------------------------------

            for field, value in validated_data.items():

                setattr(
                    product,
                    field,
                    value,
                )

            product.save()

            # --------------------------------------
            # CATEGORIES
            # --------------------------------------

            if categories is not None:

                product.categories.set(
                    categories
                )

            # --------------------------------------
            # VARIANTS
            # --------------------------------------

            if variants is not None:

                old_variants = ProductVariant.objects.filter(
                    product=product
                )

                old_variant_ids = set(
                    old_variants.values_list(
                        "id",
                        flat=True,
                    )
                )

                incoming_variant_ids = {
                    variant["id"]
                    for variant in variants
                    if variant.get("id")
                }

                variants_to_delete = (
                    old_variant_ids
                    - incoming_variant_ids
                )

                if variants_to_delete:

                    has_orders = OrderItem.objects.filter(
                        variant_id__in=variants_to_delete
                    ).exists()

                    if has_orders:

                        return Response(
                            {
                                "detail": (
                                    "یکی از تنوع‌های حذف‌شده "
                                    "سابقه سفارش دارد و قابل حذف نیست."
                                )
                            },
                            status=status.HTTP_409_CONFLICT,
                        )

                    ProductVariant.objects.filter(
                        id__in=variants_to_delete,
                        product=product,
                    ).delete()

                # ----------------------------------
                # CREATE / UPDATE VARIANTS
                # ----------------------------------

                for variant_data in variants:

                    variant_id = variant_data.pop(
                        "id",
                        None,
                    )

                    if variant_id:

                        variant = get_object_or_404(
                            ProductVariant,
                            pk=variant_id,
                            product=product,
                        )

                        for field, value in variant_data.items():

                            setattr(
                                variant,
                                field,
                                value,
                            )

                        variant.save()

                    else:

                        ProductVariant.objects.create(
                            product=product,
                            **variant_data,
                        )

            # --------------------------------------
            # FEATURES
            # --------------------------------------

            if feature_values is not None:

                FeatureValue.objects.filter(
                    product=product
                ).delete()

                FeatureValue.objects.bulk_create(
                    [
                        FeatureValue(
                            product=product,
                            feature=feature["feature"],
                            value=feature["value"],
                        )
                        for feature in feature_values
                    ]
                )

            # --------------------------------------
            # SIZE GUIDES
            # --------------------------------------

            if size_guides is not None:

                SizeGuide.objects.filter(
                    product=product
                ).delete()

                SizeGuide.objects.bulk_create(
                    [
                        SizeGuide(
                            product=product,
                            feature=size_guide.get(
                                "feature"
                            ),
                            value=size_guide.get(
                                "value"
                            ),
                            image=size_guide.get(
                                "image"
                            ),
                        )
                        for size_guide in size_guides
                    ]
                )

        product = get_product_queryset().get(
            pk=product.pk
        )

        response_serializer = AdminProductDetailSerializer(
            product,
            context={
                "request": request
            },
        )

        return Response(
            response_serializer.data
        )

    # ======================================================
    # DELETE
    # ======================================================

    @extend_schema(
        tags=["Admin - Products"],
        summary="حذف محصول",
        responses={
            204: OpenApiResponse(
                description="محصول با موفقیت حذف شد."
            ),
            409: OpenApiResponse(
                description="محصول سابقه سفارش دارد."
            ),
        },
    )
    def delete(self, request, pk):

        product = self.get_object(pk)

        # ------------------------------------------
        # ORDER HISTORY PROTECTION
        # ------------------------------------------

        has_orders = OrderItem.objects.filter(
            variant__product=product
        ).exists()

        if has_orders:

            return Response(
                {
                    "detail": (
                        "این محصول دارای سابقه سفارش است "
                        "و قابل حذف نیست."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        product.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ==========================================================
# PRODUCT STATUS
# ==========================================================

class AdminProductStatusAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    @extend_schema(
        tags=["Admin - Products"],
        summary="تغییر وضعیت محصول",
        request=AdminProductStatusSerializer,
        responses={
            200: AdminProductDetailSerializer,
        },
    )
    def patch(self, request, pk):

        product = get_object_or_404(
            Product,
            pk=pk,
        )

        serializer = AdminProductStatusSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        product.status = serializer.validated_data[
            "status"
        ]

        product.save(
            update_fields=[
                "status",
                "updated_date",
            ]
        )

        product = get_product_queryset().get(
            pk=product.pk
        )

        response_serializer = AdminProductDetailSerializer(
            product,
            context={
                "request": request
            },
        )

        return Response(
            response_serializer.data
        )


# ==========================================================
# PRODUCT IMAGE UPLOAD
# ==========================================================

class AdminProductImageUploadAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    @extend_schema(
        tags=["Admin - Products"],
        summary="افزودن تصویر محصول",
        request=AdminProductImageUploadSerializer,
        responses={
            201: AdminProductImageSerializer,
        },
    )
    def post(self, request, pk):

        product = get_object_or_404(
            Product,
            pk=pk,
        )

        serializer = AdminProductImageUploadSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        is_main = serializer.validated_data.get(
            "is_main",
            False,
        )

        # ------------------------------------------
        # IF NEW IMAGE IS MAIN
        # ------------------------------------------

        if is_main:

            ProductImages.objects.filter(
                product=product,
                is_main=True,
            ).update(
                is_main=False
            )

        image = ProductImages.objects.create(
            product=product,
            image=serializer.validated_data["image"],
            is_main=is_main,
        )

        response_serializer = AdminProductImageSerializer(
            image,
            context={
                "request": request
            },
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# PRODUCT IMAGE DELETE
# ==========================================================

class AdminProductImageDeleteAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    @extend_schema(
        tags=["Admin - Products"],
        summary="حذف تصویر محصول",
        responses={
            204: OpenApiResponse(
                description="تصویر حذف شد."
            ),
            404: OpenApiResponse(
                description="تصویر پیدا نشد."
            ),
        },
    )
    def delete(
        self,
        request,
        pk,
        image_id,
    ):

        image = get_object_or_404(
            ProductImages,
            pk=image_id,
            product_id=pk,
        )

        image.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# ==========================================================
# SET MAIN IMAGE
# ==========================================================

class AdminProductImageMainAPIView(APIView):

    permission_classes = [
        IsAdminPanelUser
    ]

    @extend_schema(
        tags=["Admin - Products"],
        summary="تعیین تصویر اصلی محصول",
        responses={
            200: AdminProductImageSerializer,
        },
    )
    def patch(
        self,
        request,
        pk,
        image_id,
    ):

        image = get_object_or_404(
            ProductImages,
            pk=image_id,
            product_id=pk,
        )

        with transaction.atomic():

            ProductImages.objects.filter(
                product_id=pk,
                is_main=True,
            ).exclude(
                pk=image.pk
            ).update(
                is_main=False
            )

            image.is_main = True

            image.save(
                update_fields=[
                    "is_main",
                    "updated_date",
                ]
            )

        serializer = AdminProductImageSerializer(
            image,
            context={
                "request": request
            },
        )

        return Response(
            serializer.data
        )
        


class AdminProductCategoryUpdateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ویرایش دسته‌بندی",
        request=AdminProductCategoryUpdateSerializer,
        responses={200: AdminProductCategorySerializer},
    )
    def patch(self, request, pk):
        category = get_object_or_404(
            ProductCategory,
            pk=pk,
        )

        serializer = AdminProductCategoryUpdateSerializer(
            category,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(
            AdminProductCategorySerializer(category).data
        )

    def delete(self, request, pk):
        category = get_object_or_404(
            ProductCategory,
            pk=pk,
        )

        if category.products.exists():
            return Response(
                {
                    "detail": "این دسته‌بندی به یک یا چند محصول متصل است و قابل حذف نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if category.children.exists():
            return Response(
                {
                    "detail": "این دسته‌بندی دارای زیرمجموعه است و قابل حذف نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        category_id = category.id
        category.delete()

        return Response(
            {
                "id": category_id,
                "message": "دسته‌بندی با موفقیت حذف شد.",
            },
            status=status.HTTP_200_OK,
        )
class AdminProductSizeUpdateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ویرایش سایز",
        request=AdminProductSizeUpdateSerializer,
        responses={200: AdminProductSizeUpdateSerializer},
    )
    def patch(self, request, pk):
        size = get_object_or_404(
            ProductSize,
            pk=pk,
        )

        serializer = AdminProductSizeUpdateSerializer(
            size,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        size = serializer.save()

        return Response(
            AdminProductSizeUpdateSerializer(size).data
        )

    def delete(self, request, pk):
        size = get_object_or_404(
            ProductSize,
            pk=pk,
        )

        if size.variants.exists():
            return Response(
                {
                    "detail": "این سایز در یک یا چند تنوع محصول استفاده شده و قابل حذف نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        size_id = size.id
        size.delete()

        return Response(
            {
                "id": size_id,
                "message": "سایز با موفقیت حذف شد.",
            },
            status=status.HTTP_200_OK,
        )
        
class AdminProductColorUpdateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ویرایش رنگ",
        request=AdminProductColorUpdateSerializer,
        responses={200: AdminProductColorUpdateSerializer},
    )
    def patch(self, request, pk):
        color = get_object_or_404(
            ProductColor,
            pk=pk,
        )

        serializer = AdminProductColorUpdateSerializer(
            color,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        color = serializer.save()

        return Response(
            AdminProductColorUpdateSerializer(color).data
        )

    def delete(self, request, pk):
        color = get_object_or_404(
            ProductColor,
            pk=pk,
        )

        if color.variants.exists():
            return Response(
                {
                    "detail": "این رنگ در یک یا چند تنوع محصول استفاده شده و قابل حذف نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        color_id = color.id
        color.delete()

        return Response(
            {
                "id": color_id,
                "message": "رنگ با موفقیت حذف شد.",
            },
            status=status.HTTP_200_OK,
        )
        
class AdminProductFeatureUpdateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin - Products"],
        summary="ویرایش ویژگی",
        request=AdminProductFeatureUpdateSerializer,
        responses={200: AdminProductFeatureUpdateSerializer},
    )
    def patch(self, request, pk):
        feature = get_object_or_404(
            Feature,
            pk=pk,
        )

        serializer = AdminProductFeatureUpdateSerializer(
            feature,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        feature = serializer.save()

        return Response(
            AdminProductFeatureUpdateSerializer(feature).data
        )

    def delete(self, request, pk):
        feature = get_object_or_404(
            Feature,
            pk=pk,
        )

        if ProductVariant.objects.filter(feature=feature).exists():
            return Response(
                {
                    "detail": "این ویژگی در یک یا چند محصول استفاده شده و قابل حذف نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        feature_id = feature.id
        feature.delete()

        return Response(
            {
                "id": feature_id,
                "message": "ویژگی با موفقیت حذف شد.",
            },
            status=status.HTTP_200_OK,
        )