from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)

from admin_panel.permissions import IsAdminPanelUser

from review.models import Review

from admin_panel.serializers.reviews import (
    AdminReviewListSerializer,
    AdminReviewDetailSerializer,
    AdminReviewCreateSerializer,
    AdminReviewUpdateSerializer,
)


# =========================================================
# LIST
# =========================================================

class AdminReviewListAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="لیست نظرات",
        description="دریافت لیست نظرات برای پنل مدیریت.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                required=False,
                description=(
                    "جستجو بر اساس شماره موبایل کاربر، "
                    "نام محصول یا متن نظر."
                ),
            ),
            OpenApiParameter(
                name="rating",
                type=OpenApiTypes.INT,
                required=False,
                description="فیلتر بر اساس امتیاز از 1 تا 5.",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                required=False,
                description="فیلتر بر اساس شناسه کاربر.",
            ),
            OpenApiParameter(
                name="product_id",
                type=OpenApiTypes.INT,
                required=False,
                description="فیلتر بر اساس شناسه محصول.",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                required=False,
                description=(
                    "مرتب‌سازی: "
                    "created_date یا -created_date"
                ),
            ),
        ],
        responses=AdminReviewListSerializer(many=True),
        tags=["Admin Panel - Reviews"],
    )
    def get(self, request):
        queryset = Review.objects.select_related(
            "user",
            "product",
        )

        search = request.query_params.get("search")
        rating = request.query_params.get("rating")
        user_id = request.query_params.get("user_id")
        product_id = request.query_params.get("product_id")
        ordering = request.query_params.get(
            "ordering",
            "-created_date",
        )

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        if search:
            queryset = queryset.filter(
                Q(user__phone_number__icontains=search)
                | Q(product__title__icontains=search)
                | Q(comment__icontains=search)
            )

        # -------------------------------------------------
        # RATING
        # -------------------------------------------------

        if rating:
            try:
                rating = int(rating)

                if 1 <= rating <= 5:
                    queryset = queryset.filter(
                        rating=rating
                    )

            except (TypeError, ValueError):
                pass

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        if user_id:
            queryset = queryset.filter(
                user_id=user_id
            )

        # -------------------------------------------------
        # PRODUCT
        # -------------------------------------------------

        if product_id:
            queryset = queryset.filter(
                product_id=product_id
            )

        # -------------------------------------------------
        # ORDERING
        # -------------------------------------------------

        allowed_ordering = (
            "created_date",
            "-created_date",
            "updated_date",
            "-updated_date",
            "rating",
            "-rating",
        )

        if ordering not in allowed_ordering:
            ordering = "-created_date"

        queryset = queryset.order_by(ordering)

        serializer = AdminReviewListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)


# =========================================================
# CREATE
# =========================================================

class AdminReviewCreateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="ایجاد نظر",
        description="ایجاد یک نظر جدید توسط ادمین.",
        request=AdminReviewCreateSerializer,
        responses={
            201: AdminReviewDetailSerializer,
        },
        tags=["Admin Panel - Reviews"],
    )
    def post(self, request):
        serializer = AdminReviewCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        review = serializer.save()

        response_serializer = AdminReviewDetailSerializer(
            review
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# DETAIL
# =========================================================

class AdminReviewDetailAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="جزئیات نظر",
        description="دریافت جزئیات یک نظر.",
        responses=AdminReviewDetailSerializer,
        tags=["Admin Panel - Reviews"],
    )
    def get(self, request, pk):
        try:
            review = Review.objects.select_related(
                "user",
                "product",
            ).get(pk=pk)

        except Review.DoesNotExist:
            return Response(
                {
                    "detail": "نظر مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminReviewDetailSerializer(
            review
        )

        return Response(serializer.data)


# =========================================================
# UPDATE
# =========================================================

class AdminReviewUpdateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="ویرایش نظر",
        description="ویرایش کامل یا جزئی یک نظر.",
        request=AdminReviewUpdateSerializer,
        responses=AdminReviewDetailSerializer,
        tags=["Admin Panel - Reviews"],
    )
    def put(self, request, pk):
        return self._update(
            request,
            pk,
            partial=False,
        )

    def patch(self, request, pk):
        return self._update(
            request,
            pk,
            partial=True,
        )

    def _update(self, request, pk, partial=False):
        try:
            review = Review.objects.select_related(
                "user",
                "product",
            ).get(pk=pk)

        except Review.DoesNotExist:
            return Response(
                {
                    "detail": "نظر مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminReviewUpdateSerializer(
            review,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(raise_exception=True)

        review = serializer.save()

        response_serializer = AdminReviewDetailSerializer(
            review
        )

        return Response(
            response_serializer.data
        )


# =========================================================
# DELETE
# =========================================================

class AdminReviewDeleteAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="حذف نظر",
        description="حذف یک نظر از پنل مدیریت.",
        responses={
            204: None,
        },
        tags=["Admin Panel - Reviews"],
    )
    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)

        except Review.DoesNotExist:
            return Response(
                {
                    "detail": "نظر مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        review.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )