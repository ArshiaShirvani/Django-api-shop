from django.db import transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from cart.models import Cart, CartItem

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    Order,
    OrderItem,
)

from .serializers import (
    AddressSerializer,
    ShippingMethodSerializer,
    CouponApplySerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    CreateOrderSerializer,
)


# =========================================================
# Base
# =========================================================

class OrderBaseAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get_user_order_queryset(self):

        return (
            Order.objects
            .filter(
                user=self.request.user
            )
            .select_related(
                "user",
                "coupon",
                "shipping_method",
            )
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=(
                        OrderItem.objects
                        .select_related(
                            "variant__product",
                            "variant__size",
                            "variant__color",
                        )
                    ),
                )
            )
        )


# =========================================================
# Address List / Create
# =========================================================

class AddressListCreateAPIView(
    OrderBaseAPIView
):

    def get(self, request):

        addresses = (
            Address.objects
            .filter(
                user=request.user
            )
            .order_by(
                "-is_default",
                "-created_date",
            )
        )

        serializer = AddressSerializer(
            addresses,
            many=True,
        )

        return Response(
            serializer.data
        )

    def post(self, request):

        serializer = AddressSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = serializer.save(
            user=request.user
        )

        return Response(
            AddressSerializer(address).data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# Address Detail
# =========================================================

class AddressDetailAPIView(
    OrderBaseAPIView
):

    def get_object(self, request, pk):

        return get_object_or_404(
            Address,
            pk=pk,
            user=request.user,
        )

    def get(self, request, pk):

        address = self.get_object(
            request,
            pk,
        )

        return Response(
            AddressSerializer(
                address
            ).data
        )

    def patch(self, request, pk):

        address = self.get_object(
            request,
            pk,
        )

        serializer = AddressSerializer(
            address,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )

    def delete(self, request, pk):

        address = self.get_object(
            request,
            pk,
        )

        address.delete()

        return Response(
            {
                "detail": "آدرس با موفقیت حذف شد."
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Shipping Methods
# =========================================================

class ShippingMethodListAPIView(
    OrderBaseAPIView
):

    def get(self, request):

        cart = (
            Cart.objects
            .filter(
                user=request.user
            )
            .prefetch_related(
                "items__variant__product",
            )
            .first()
        )

        subtotal = 0

        if cart:

            subtotal = sum(
                item.subtotal
                for item in cart.items.all()
            )

        methods = (
            ShippingMethod.objects
            .filter(
                is_active=True
            )
            .order_by(
                "display_order",
                "id",
            )
        )

        serializer = ShippingMethodSerializer(
            methods,
            many=True,
            context={
                "request": request,
                "subtotal": subtotal,
            },
        )

        return Response(
            {
                "subtotal": subtotal,
                "shipping_methods": serializer.data,
            }
        )


# =========================================================
# Coupon Apply
# =========================================================

class CouponApplyAPIView(
    OrderBaseAPIView
):

    def post(self, request):

        serializer = CouponApplySerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        code = serializer.validated_data["code"]

        coupon = (
            Coupon.objects
            .filter(
                code=code
            )
            .first()
        )

        if not coupon:

            return Response(
                {
                    "detail": "کد تخفیف معتبر نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Time / Active
        # -------------------------------------------------

        if not coupon.is_valid_time:

            return Response(
                {
                    "detail": (
                        "این کد تخفیف در حال حاضر فعال نیست."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Allowed Users
        # -------------------------------------------------

        if not coupon.is_available_for_user(
            request.user
        ):

            return Response(
                {
                    "detail": (
                        "شما مجاز به استفاده از "
                        "این کد تخفیف نیستید."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Cart
        # -------------------------------------------------

        cart = (
            Cart.objects
            .filter(
                user=request.user
            )
            .prefetch_related(
                "items__variant__product",
            )
            .first()
        )

        if not cart or not cart.items.exists():

            return Response(
                {
                    "detail": "سبد خرید شما خالی است."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Stock + Subtotal
        # -------------------------------------------------

        subtotal = 0

        for item in cart.items.all():

            variant = item.variant

            if not variant.is_active:

                return Response(
                    {
                        "detail": (
                            f"محصول «{variant.product.title}» "
                            "دیگر فعال نیست."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if variant.stock <= 0:

                return Response(
                    {
                        "detail": (
                            f"محصول «{variant.product.title}» "
                            "ناموجود است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if item.quantity > variant.stock:

                return Response(
                    {
                        "detail": (
                            f"موجودی محصول "
                            f"«{variant.product.title}» "
                            f"فقط {variant.stock} عدد است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subtotal += (
                variant.final_price
                * item.quantity
            )

        # -------------------------------------------------
        # Minimum Order
        # -------------------------------------------------

        if subtotal < coupon.minimum_order_amount:

            return Response(
                {
                    "detail": (
                        "حداقل مبلغ سفارش برای "
                        "استفاده از این کد تخفیف "
                        f"{coupon.minimum_order_amount:,} تومان است."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Per User Usage
        # -------------------------------------------------

        user_usage_count = (
            coupon.usages
            .filter(
                user=request.user
            )
            .count()
        )

        if (
            user_usage_count
            >= coupon.usage_limit_per_user
        ):

            return Response(
                {
                    "detail": (
                        "شما قبلاً به حداکثر "
                        "دفعات مجاز استفاده از "
                        "این کد تخفیف رسیده‌اید."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Global Usage
        # -------------------------------------------------

        if coupon.usage_limit is not None:

            total_usage = coupon.usages.count()

            if total_usage >= coupon.usage_limit:

                return Response(
                    {
                        "detail": (
                            "ظرفیت استفاده از این "
                            "کد تخفیف تکمیل شده است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -------------------------------------------------
        # Calculate Discount
        # -------------------------------------------------

        discount = coupon.calculate_discount(
            subtotal
        )

        final_price = max(
            subtotal - discount,
            0,
        )

        return Response(
            {
                "valid": True,
                "code": coupon.code,
                "discount_type": coupon.discount_type,
                "discount_value": coupon.discount_value,
                "discount_amount": discount,
                "subtotal": subtotal,
                "final_price": final_price,
            }
        )


# =========================================================
# Create Order
# =========================================================

class OrderCreateAPIView(
    OrderBaseAPIView
):

    @transaction.atomic
    def post(self, request):

        # =================================================
        # Validate Request
        # =================================================

        serializer = CreateOrderSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        address_id = (
            serializer.validated_data[
                "address_id"
            ]
        )

        shipping_method_id = (
            serializer.validated_data[
                "shipping_method_id"
            ]
        )

        coupon_code = (
            serializer.validated_data.get(
                "coupon_code"
            )
        )

        # =================================================
        # Profile Validation
        # =================================================

        profile = getattr(
            request.user,
            "profile",
            None,
        )

        if not profile:

            return Response(
                {
                    "detail": (
                        "پروفایل شما کامل نیست. "
                        "لطفاً ابتدا پروفایل خود را تکمیل کنید."
                    ),
                    "code": "PROFILE_REQUIRED",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not profile.first_name
            or not profile.last_name
        ):

            return Response(
                {
                    "detail": (
                        "نام و نام خانوادگی شما کامل نیست. "
                        "لطفاً ابتدا پروفایل خود را تکمیل کنید."
                    ),
                    "code": "PROFILE_INCOMPLETE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Address
        # =================================================

        address = get_object_or_404(
            Address,
            pk=address_id,
            user=request.user,
        )

        # =================================================
        # Shipping
        # =================================================

        shipping_method = get_object_or_404(
            ShippingMethod,
            pk=shipping_method_id,
            is_active=True,
        )

        # =================================================
        # Lock Cart
        # =================================================

        cart = (
            Cart.objects
            .select_for_update()
            .filter(
                user=request.user
            )
            .first()
        )

        if not cart:

            return Response(
                {
                    "detail": (
                        "سبد خرید شما وجود ندارد."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = list(
            CartItem.objects
            .select_for_update()
            .select_related(
                "variant__product",
                "variant__size",
                "variant__color",
            )
            .filter(
                cart=cart
            )
        )

        if not cart_items:

            return Response(
                {
                    "detail": (
                        "سبد خرید شما خالی است."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Validate Products + Calculate Subtotal
        # =================================================

        subtotal = 0

        for item in cart_items:

            variant = item.variant

            if not variant.is_active:

                return Response(
                    {
                        "detail": (
                            f"محصول «{variant.product.title}» "
                            "دیگر فعال نیست."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if variant.stock <= 0:

                return Response(
                    {
                        "detail": (
                            f"محصول «{variant.product.title}» "
                            "ناموجود است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if item.quantity > variant.stock:

                return Response(
                    {
                        "detail": (
                            f"موجودی محصول "
                            f"«{variant.product.title}» "
                            f"فقط {variant.stock} عدد است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subtotal += (
                variant.final_price
                * item.quantity
            )

        # =================================================
        # Coupon
        # =================================================

        coupon = None
        coupon_discount = 0
        normalized_coupon_code = ""

        if coupon_code:

            normalized_coupon_code = (
                coupon_code.strip().upper()
            )

            coupon = (
                Coupon.objects
                .select_for_update()
                .filter(
                    code=normalized_coupon_code
                )
                .first()
            )

            if not coupon:

                return Response(
                    {
                        "detail": (
                            "کد تخفیف معتبر نیست."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ---------------------------------------------
            # Active / Time
            # ---------------------------------------------

            if not coupon.is_valid_time:

                return Response(
                    {
                        "detail": (
                            "کد تخفیف منقضی شده "
                            "یا هنوز فعال نشده است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ---------------------------------------------
            # Allowed Users
            # ---------------------------------------------

            if not coupon.is_available_for_user(
                request.user
            ):

                return Response(
                    {
                        "detail": (
                            "شما مجاز به استفاده از "
                            "این کد تخفیف نیستید."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ---------------------------------------------
            # Per User Limit
            # ---------------------------------------------

            user_usage_count = (
                coupon.usages
                .filter(
                    user=request.user
                )
                .count()
            )

            if (
                user_usage_count
                >= coupon.usage_limit_per_user
            ):

                return Response(
                    {
                        "detail": (
                            "شما دیگر مجاز به استفاده "
                            "از این کد تخفیف نیستید."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ---------------------------------------------
            # Global Limit
            # ---------------------------------------------

            if coupon.usage_limit is not None:

                total_usage = coupon.usages.count()

                if total_usage >= coupon.usage_limit:

                    return Response(
                        {
                            "detail": (
                                "ظرفیت استفاده از "
                                "این کد تخفیف تکمیل شده است."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # ---------------------------------------------
            # Minimum Order
            # ---------------------------------------------

            if (
                subtotal
                < coupon.minimum_order_amount
            ):

                return Response(
                    {
                        "detail": (
                            "مبلغ سبد خرید شما "
                            "به حداقل مبلغ لازم "
                            "برای این کد تخفیف نمی‌رسد."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            coupon_discount = (
                coupon.calculate_discount(
                    subtotal
                )
            )

        # =================================================
        # Shipping Cost
        # =================================================

        shipping_cost = (
            shipping_method.calculate_cost(
                subtotal
            )
        )

        # =================================================
        # Final Price
        # =================================================

        total_price = max(
            subtotal
            - coupon_discount
            + shipping_cost,
            0,
        )

        # =================================================
        # Create Order
        # =================================================
        #
        # IMPORTANT:
        # در این مرحله موجودی کم نمی‌شود.
        #
        # موجودی فقط بعد از پرداخت موفق
        # در Payment کم خواهد شد.
        #
        # =================================================

        order = Order.objects.create(

            user=request.user,

            status=Order.Status.PENDING,

            coupon=coupon,

            coupon_code=(
                normalized_coupon_code
                if coupon
                else ""
            ),

            coupon_discount=coupon_discount,

            shipping_method=shipping_method,

            shipping_title=shipping_method.title,

            shipping_cost=shipping_cost,

            # ---------------------------------------------
            # Address Snapshot
            # ---------------------------------------------

            recipient_name=(
                address.recipient_name
            ),

            recipient_phone=(
                address.recipient_phone
            ),

            province=address.province,

            city=address.city,

            address=address.address,

            postal_code=address.postal_code,

            plaque=address.plaque,

            unit=address.unit,

            # ---------------------------------------------
            # Price
            # ---------------------------------------------

            subtotal=subtotal,

            discount_amount=coupon_discount,

            total_price=total_price,
        )

        # =================================================
        # Create Order Items
        # =================================================
        #
        # فقط Snapshot می‌گیریم.
        # موجودی اینجا تغییر نمی‌کند.
        #
        # =================================================

        for item in cart_items:

            variant = item.variant

            unit_price = variant.final_price

            OrderItem.objects.create(

                order=order,

                variant=variant,

                # -----------------------------------------
                # Product Snapshot
                # -----------------------------------------

                product_title=(
                    variant.product.title
                ),

                sku=variant.sku,

                size=(
                    variant.size.title
                    if variant.size
                    else ""
                ),

                color=(
                    variant.color.title
                    if variant.color
                    else ""
                ),

                color_code=(
                    variant.color.code
                    if variant.color
                    else ""
                ),

                # -----------------------------------------
                # Price Snapshot
                # -----------------------------------------

                original_unit_price=(
                    variant.price
                ),

                discount_percent=(
                    variant.discount_percent
                ),

                unit_price=unit_price,

                quantity=item.quantity,

                subtotal=(
                    unit_price
                    * item.quantity
                ),
            )

        # =================================================
        # Clear Cart
        # =================================================

        CartItem.objects.filter(
            cart=cart
        ).delete()

        # =================================================
        # Response
        # =================================================

        return Response(
            {
                "detail": (
                    "سفارش با موفقیت ایجاد شد."
                ),

                "order": OrderDetailSerializer(
                    order,
                    context={
                        "request": request,
                    },
                ).data,

                "next_step": "payment",
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# My Orders
# =========================================================

class MyOrdersAPIView(
    OrderBaseAPIView
):

    def get(self, request):

        orders = (
            self.get_user_order_queryset()
            .annotate(
                items_count=Count(
                    "items"
                )
            )
        )

        serializer = OrderListSerializer(
            orders,
            many=True,
        )

        return Response(
            serializer.data
        )


# =========================================================
# Order Detail
# =========================================================

class OrderDetailAPIView(
    OrderBaseAPIView
):

    def get(self, request, order_number):

        order = get_object_or_404(
            self.get_user_order_queryset(),
            order_number=order_number,
        )

        serializer = OrderDetailSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data
        )


# =========================================================
# Cancel Order
# =========================================================

class OrderCancelAPIView(
    OrderBaseAPIView
):

    @transaction.atomic
    def post(self, request, order_number):

        order = get_object_or_404(
            Order.objects
            .select_for_update()
            .filter(
                user=request.user
            ),
            order_number=order_number,
        )

        # -------------------------------------------------
        # Only Pending orders
        # -------------------------------------------------

        if order.status != Order.Status.PENDING:

            return Response(
                {
                    "detail": (
                        "این سفارش در وضعیت فعلی "
                        "قابل لغو نیست."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Cancel
        # -------------------------------------------------
        #
        # IMPORTANT:
        # در زمان Create Order موجودی کم نشده،
        # بنابراین هنگام Cancel چیزی هم برنمی‌گردانیم.
        #
        # -------------------------------------------------

        order.status = (
            Order.Status.CANCELLED
        )

        order.cancelled_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_date",
            ],
        )

        return Response(
            {
                "detail": (
                    "سفارش با موفقیت لغو شد."
                )
            },
            status=status.HTTP_200_OK,
        )