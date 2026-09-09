from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from accounts.models import Profile

from order.models import Address, Order

from shop.models import Product

from .models import Favorite

from .serializers import (
    DashboardProfileSerializer,
    DashboardAddressSerializer,
    DashboardOrderSerializer,
    FavoriteSerializer,
    FavoriteCreateSerializer,
)


# =========================================================
# PROFILE
# =========================================================

class DashboardProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="دریافت پروفایل",
        responses={
            200: DashboardProfileSerializer,
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def get(self, request):

        profile, created = Profile.objects.get_or_create(
            user=request.user,
        )

        serializer = DashboardProfileSerializer(
            profile,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Dashboard"],
        summary="ویرایش پروفایل",
        request=DashboardProfileSerializer,
        responses={
            200: DashboardProfileSerializer,
            400: OpenApiResponse(
                description="اطلاعات نامعتبر است.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def patch(self, request):

        profile, created = Profile.objects.get_or_create(
            user=request.user,
        )

        serializer = DashboardProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# ORDERS LIST
# =========================================================

class DashboardOrderListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="لیست سفارش‌های کاربر",
        responses={
            200: DashboardOrderSerializer(many=True),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def get(self, request):

        orders = (
            Order.objects
            .filter(
                user=request.user,
            )
            .select_related(
                "shipping_method",
                "coupon",
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_date",
            )
        )

        serializer = DashboardOrderSerializer(
            orders,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# ORDER DETAIL
# =========================================================

class DashboardOrderDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="جزئیات سفارش",
        responses={
            200: DashboardOrderSerializer,
            404: OpenApiResponse(
                description="سفارش پیدا نشد.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def get(self, request, pk):

        try:
            order = (
                Order.objects
                .select_related(
                    "shipping_method",
                    "coupon",
                )
                .prefetch_related(
                    "items",
                )
                .get(
                    id=pk,
                    user=request.user,
                )
            )

        except Order.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "سفارش مورد نظر پیدا نشد.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DashboardOrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# ADDRESSES LIST + CREATE
# =========================================================

class DashboardAddressListCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="لیست آدرس‌ها",
        responses={
            200: DashboardAddressSerializer(many=True),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def get(self, request):

        addresses = (
            Address.objects
            .filter(
                user=request.user,
            )
            .order_by(
                "-is_default",
                "-created_date",
            )
        )

        serializer = DashboardAddressSerializer(
            addresses,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Dashboard"],
        summary="ایجاد آدرس جدید",
        request=DashboardAddressSerializer,
        responses={
            201: DashboardAddressSerializer,
            400: OpenApiResponse(
                description="اطلاعات آدرس نامعتبر است.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def post(self, request):

        serializer = DashboardAddressSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        address = serializer.save()

        return Response(
            DashboardAddressSerializer(
                address,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# ADDRESS DETAIL
# =========================================================

class DashboardAddressDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):

        try:
            return Address.objects.get(
                id=pk,
                user=request.user,
            )

        except Address.DoesNotExist:
            return None

    @extend_schema(
        tags=["Dashboard"],
        summary="دریافت آدرس",
        responses={
            200: DashboardAddressSerializer,
            404: OpenApiResponse(
                description="آدرس پیدا نشد.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def get(self, request, pk):

        address = self.get_object(
            request,
            pk,
        )

        if not address:

            return Response(
                {
                    "success": False,
                    "message": "آدرس مورد نظر پیدا نشد.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DashboardAddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Dashboard"],
        summary="ویرایش آدرس",
        request=DashboardAddressSerializer,
        responses={
            200: DashboardAddressSerializer,
            400: OpenApiResponse(
                description="اطلاعات آدرس نامعتبر است.",
            ),
            404: OpenApiResponse(
                description="آدرس پیدا نشد.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def patch(self, request, pk):

        address = self.get_object(
            request,
            pk,
        )

        if not address:

            return Response(
                {
                    "success": False,
                    "message": "آدرس مورد نظر پیدا نشد.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DashboardAddressSerializer(
            address,
            data=request.data,
            partial=True,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Dashboard"],
        summary="حذف آدرس",
        responses={
            204: OpenApiResponse(
                description="آدرس با موفقیت حذف شد.",
            ),
            404: OpenApiResponse(
                description="آدرس پیدا نشد.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def delete(self, request, pk):

        address = self.get_object(
            request,
            pk,
        )

        if not address:

            return Response(
                {
                    "success": False,
                    "message": "آدرس مورد نظر پیدا نشد.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        address.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================================================
# FAVORITES LIST + CREATE
# =========================================================

class DashboardFavoriteListCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="لیست علاقه‌مندی‌ها",
        responses={
            200: FavoriteSerializer(many=True),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def get(self, request):

        favorites = (
            Favorite.objects
            .filter(
                user=request.user,
            )
            .select_related(
                "product",
            )
            .prefetch_related(
                "product__categories",
            )
            .order_by(
                "-created_date",
            )
        )

        serializer = FavoriteSerializer(
            favorites,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Dashboard"],
        summary="افزودن محصول به علاقه‌مندی",
        request=FavoriteCreateSerializer,
        responses={
            201: FavoriteSerializer,
            400: OpenApiResponse(
                description="محصول نامعتبر یا قبلاً اضافه شده است.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def post(self, request):

        serializer = FavoriteCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        product_id = serializer.validated_data[
            "product_id"
        ]

        product = Product.objects.get(
            id=product_id,
        )

        favorite = Favorite.objects.create(
            user=request.user,
            product=product,
        )

        return Response(
            FavoriteSerializer(
                favorite,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# FAVORITE DELETE
# =========================================================

class DashboardFavoriteDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="حذف محصول از علاقه‌مندی",
        responses={
            204: OpenApiResponse(
                description="محصول از علاقه‌مندی‌ها حذف شد.",
            ),
            404: OpenApiResponse(
                description="محصول در علاقه‌مندی‌ها پیدا نشد.",
            ),
            401: OpenApiResponse(
                description="کاربر احراز هویت نشده است.",
            ),
        },
    )
    def delete(self, request, product_id):

        try:
            favorite = Favorite.objects.get(
                user=request.user,
                product_id=product_id,
            )

        except Favorite.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این محصول در علاقه‌مندی‌های "
                        "شما وجود ندارد."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        favorite.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )