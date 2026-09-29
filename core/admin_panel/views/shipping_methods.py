from django.db.models import Q
from django.db.models.deletion import ProtectedError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)

from admin_panel.permissions import IsAdminPanelUser

from order.models import ShippingMethod

from admin_panel.serializers.shipping_methods import (
    AdminShippingMethodListSerializer,
    AdminShippingMethodDetailSerializer,
    AdminShippingMethodCreateSerializer,
    AdminShippingMethodUpdateSerializer,
)


# =========================================================
# LIST
# =========================================================

class AdminShippingMethodListAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="لیست روش‌های ارسال",
        description="دریافت لیست روش‌های ارسال برای پنل مدیریت.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                required=False,
                description="جستجو بر اساس عنوان یا کد روش ارسال.",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                required=False,
                description="فیلتر بر اساس فعال یا غیرفعال بودن.",
            ),
        ],
        responses=AdminShippingMethodListSerializer(many=True),
        tags=["Admin Panel - Shipping Methods"],
    )
    def get(self, request):
        queryset = ShippingMethod.objects.all()

        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(code__icontains=search)
            )

        if is_active is not None:
            if is_active.lower() in ("true", "1"):
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() in ("false", "0"):
                queryset = queryset.filter(is_active=False)

        queryset = queryset.order_by(
            "display_order",
            "-created_date",
        )

        serializer = AdminShippingMethodListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)


# =========================================================
# CREATE
# =========================================================

class AdminShippingMethodCreateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="ایجاد روش ارسال",
        description="ایجاد یک روش ارسال جدید در پنل مدیریت.",
        request=AdminShippingMethodCreateSerializer,
        responses={
            201: AdminShippingMethodDetailSerializer,
        },
        tags=["Admin Panel - Shipping Methods"],
    )
    def post(self, request):
        serializer = AdminShippingMethodCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        shipping_method = serializer.save()

        response_serializer = AdminShippingMethodDetailSerializer(
            shipping_method
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# DETAIL
# =========================================================

class AdminShippingMethodDetailAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="جزئیات روش ارسال",
        description="دریافت جزئیات یک روش ارسال.",
        responses=AdminShippingMethodDetailSerializer,
        tags=["Admin Panel - Shipping Methods"],
    )
    def get(self, request, pk):
        try:
            shipping_method = ShippingMethod.objects.get(pk=pk)

        except ShippingMethod.DoesNotExist:
            return Response(
                {
                    "detail": "روش ارسال مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminShippingMethodDetailSerializer(
            shipping_method
        )

        return Response(serializer.data)


# =========================================================
# UPDATE
# =========================================================

class AdminShippingMethodUpdateAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="ویرایش روش ارسال",
        description="ویرایش کامل یا جزئی یک روش ارسال.",
        request=AdminShippingMethodUpdateSerializer,
        responses=AdminShippingMethodDetailSerializer,
        tags=["Admin Panel - Shipping Methods"],
    )
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial=False):
        try:
            shipping_method = ShippingMethod.objects.get(pk=pk)

        except ShippingMethod.DoesNotExist:
            return Response(
                {
                    "detail": "روش ارسال مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminShippingMethodUpdateSerializer(
            shipping_method,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(raise_exception=True)

        shipping_method = serializer.save()

        response_serializer = AdminShippingMethodDetailSerializer(
            shipping_method
        )

        return Response(response_serializer.data)


# =========================================================
# DELETE
# =========================================================

class AdminShippingMethodDeleteAPIView(APIView):
    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        summary="حذف روش ارسال",
        description="حذف یک روش ارسال از پنل مدیریت.",
        responses={
            204: None,
        },
        tags=["Admin Panel - Shipping Methods"],
    )
    def delete(self, request, pk):
        try:
            shipping_method = ShippingMethod.objects.get(pk=pk)

        except ShippingMethod.DoesNotExist:
            return Response(
                {
                    "detail": "روش ارسال مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            shipping_method.delete()

        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "این روش ارسال در سفارش‌ها استفاده شده "
                        "و قابل حذف نیست."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )