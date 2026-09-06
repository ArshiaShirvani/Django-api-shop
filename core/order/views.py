from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    Order,
)
from .serializers import (
    AddressSerializer,
    ShippingMethodSerializer,
    CouponApplySerializer,
    OrderSerializer,
    OrderCreateSerializer,
)
from .services import OrderService


# =========================================================
# ADDRESS
# =========================================================

@extend_schema(
    tags=["Address"],
)
class AddressListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست آدرس‌های کاربر",
        description="تمام آدرس‌های متعلق به کاربر فعلی را برمی‌گرداند.",
        responses=AddressSerializer(many=True),
    )
    def get(self, request):
        addresses = (
            Address.objects
            .filter(user=request.user)
            .order_by("-is_default", "-created_date")
        )

        serializer = AddressSerializer(
            addresses,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="ایجاد آدرس جدید",
        description="یک آدرس جدید برای کاربر فعلی ایجاد می‌کند.",
        request=AddressSerializer,
        responses={
            201: AddressSerializer,
            400: OpenApiResponse(
                description="اطلاعات ارسال‌شده معتبر نیست."
            ),
        },
    )
    def post(self, request):
        serializer = AddressSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        address = serializer.save()

        response_serializer = AddressSerializer(
            address,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Address"],
)
class AddressDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(
            Address,
            pk=pk,
            user=request.user,
        )

    @extend_schema(
        summary="ویرایش آدرس",
        description="آدرس انتخاب‌شده را ویرایش می‌کند.",
        request=AddressSerializer,
        responses={
            200: AddressSerializer,
            400: OpenApiResponse(
                description="اطلاعات ارسال‌شده معتبر نیست."
            ),
            404: OpenApiResponse(
                description="آدرس پیدا نشد."
            ),
        },
    )
    def patch(self, request, pk):
        address = self.get_object(request, pk)

        serializer = AddressSerializer(
            address,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        address = serializer.save()

        response_serializer = AddressSerializer(
            address,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="حذف آدرس",
        description="آدرس انتخاب‌شده را حذف می‌کند.",
        responses={
            204: OpenApiResponse(
                description="آدرس با موفقیت حذف شد."
            ),
            404: OpenApiResponse(
                description="آدرس پیدا نشد."
            ),
        },
    )
    def delete(self, request, pk):
        address = self.get_object(request, pk)

        address.delete()

        return Response(
            {"detail": "آدرس با موفقیت حذف شد."},
            status=status.HTTP_204_NO_CONTENT,
        )


# =========================================================
# SHIPPING METHODS
# =========================================================

@extend_schema(
    tags=["Shipping"],
)
class ShippingMethodListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست روش‌های ارسال",
        description="تمام روش‌های ارسال فعال را نمایش می‌دهد.",
        responses=ShippingMethodSerializer(many=True),
    )
    def get(self, request):
        shipping_methods = (
            ShippingMethod.objects
            .filter(is_active=True)
            .order_by("display_order", "id")
        )

        serializer = ShippingMethodSerializer(
            shipping_methods,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# COUPON
# =========================================================

@extend_schema(
    tags=["Coupon"],
)
class CouponApplyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="بررسی کد تخفیف",
        description=(
            "کد تخفیف را بررسی می‌کند. "
            "در این مرحله کد تخفیف مصرف نمی‌شود."
        ),
        request=CouponApplySerializer,
        responses={
            200: OpenApiResponse(
                description="کد تخفیف معتبر است."
            ),
            400: OpenApiResponse(
                description="کد تخفیف معتبر نیست یا قابل استفاده نیست."
            ),
        },
    )
    def post(self, request):
        serializer = CouponApplySerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data["coupon"]

        return Response(
            {
                "detail": "کد تخفیف معتبر است.",
                "code": coupon.code,
                "discount_type": coupon.discount_type,
                "discount_value": coupon.discount_value,
                "minimum_order_amount": coupon.minimum_order_amount,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# ORDER CREATE
# =========================================================

@extend_schema(
    tags=["Order"],
)
class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="ایجاد سفارش",
        description=(
            "از روی سبد خرید کاربر یک سفارش ایجاد می‌کند. "
            "آدرس و روش ارسال الزامی هستند و کد تخفیف اختیاری است."
        ),
        request=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(
                description="اطلاعات سفارش معتبر نیست."
            ),
        },
    )
    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data["address_id"]
        shipping_method_id = serializer.validated_data["shipping_method_id"]
        coupon_code = serializer.validated_data.get("coupon_code")

        address = get_object_or_404(
            Address,
            id=address_id,
            user=request.user,
        )

        shipping_method = get_object_or_404(
            ShippingMethod,
            id=shipping_method_id,
            is_active=True,
        )

        coupon = None

        if coupon_code:
            coupon = get_object_or_404(
                Coupon,
                code=coupon_code.strip().upper(),
            )

        try:
            order = OrderService.create_order(
                user=request.user,
                address=address,
                shipping_method=shipping_method,
                coupon=coupon,
            )

        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                detail = exc.message_dict
            else:
                detail = {
                    "detail": exc.messages
                }

            return Response(
                detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# MY ORDERS
# =========================================================

@extend_schema(
    tags=["Order"],
)
class MyOrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست سفارش‌های من",
        description="تمام سفارش‌های کاربر فعلی را نمایش می‌دهد.",
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .select_related(
                "coupon",
                "shipping_method",
            )
            .prefetch_related("items")
            .order_by("-created_date")
        )

        serializer = OrderSerializer(
            orders,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Order"],
)
class MyOrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="جزئیات سفارش",
        description="جزئیات یک سفارش متعلق به کاربر فعلی را نمایش می‌دهد.",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(
                description="سفارش پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects
            .select_related(
                "coupon",
                "shipping_method",
            )
            .prefetch_related("items"),
            pk=pk,
            user=request.user,
        )

        serializer = OrderSerializer(
            order,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )