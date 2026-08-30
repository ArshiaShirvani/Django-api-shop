from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from cart.models import Cart, CartItem
from shop.models import ProductVariant

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    CouponUsage,
    Order,
    OrderItem,
)


class OrderService:

    # =========================================================
    # Profile
    # =========================================================

    @staticmethod
    def validate_profile(user):
        """
        بررسی کامل بودن اطلاعات پروفایل قبل از ورود به Order.
        """

        profile = getattr(user, "profile", None)

        if profile is None:
            raise ValueError(
                "پروفایل شما ایجاد نشده است. ابتدا پروفایل خود را تکمیل کنید."
            )

        if not profile.first_name:
            raise ValueError(
                "نام شما تکمیل نشده است. ابتدا پروفایل خود را تکمیل کنید."
            )

        if not profile.last_name:
            raise ValueError(
                "نام خانوادگی شما تکمیل نشده است. ابتدا پروفایل خود را تکمیل کنید."
            )

        if not user.phone_number:
            raise ValueError(
                "شماره تلفن شما ثبت نشده است."
            )

        return profile

    # =========================================================
    # Cart
    # =========================================================

    @staticmethod
    def get_user_cart(user):
        """
        دریافت سبد خرید کاربر.
        """

        cart, _ = Cart.objects.get_or_create(
            user=user
        )

        return cart

    # =========================================================
    # Cart Validation
    # =========================================================

    @staticmethod
    def validate_cart_items(cart):
        """
        بررسی می‌کند تمام آیتم‌های سبد هنوز معتبر و دارای موجودی باشند.
        """

        items = (
            CartItem.objects
            .select_related(
                "variant",
                "variant__product",
                "variant__size",
                "variant__color",
            )
            .filter(
                cart=cart
            )
        )

        if not items.exists():
            raise ValueError(
                "سبد خرید شما خالی است."
            )

        for item in items:

            variant = item.variant

            if not variant.is_active:
                raise ValueError(
                    f"محصول «{variant.product.title}» دیگر فعال نیست."
                )

            if variant.stock <= 0:
                raise ValueError(
                    f"محصول «{variant.product.title}» موجود نیست."
                )

            if item.quantity > variant.stock:
                raise ValueError(
                    f"موجودی محصول «{variant.product.title}» کافی نیست. "
                    f"حداکثر موجودی: {variant.stock}"
                )

        return items

    # =========================================================
    # Subtotal
    # =========================================================

    @staticmethod
    def calculate_subtotal(cart):
        """
        محاسبه مبلغ کالاها با قیمت نهایی Variant.
        """

        items = (
            CartItem.objects
            .select_related(
                "variant"
            )
            .filter(
                cart=cart
            )
        )

        subtotal = 0

        for item in items:

            subtotal += (
                item.variant.final_price
                * item.quantity
            )

        return subtotal

    # =========================================================
    # Coupon
    # =========================================================

    @staticmethod
    def validate_coupon(
        user,
        code,
        subtotal,
    ):
        """
        فقط اعتبارسنجی کد تخفیف.
        اینجا CouponUsage ایجاد نمی‌شود.

        بنابراین اگر کاربر فقط کد را Apply کند
        ولی پرداخت نکند، کد مصرف‌شده محسوب نمی‌شود.
        """

        if not code:
            return None, 0

        code = code.strip().upper()

        try:

            coupon = Coupon.objects.get(
                code=code
            )

        except Coupon.DoesNotExist:

            raise ValueError(
                "کد تخفیف معتبر نیست."
            )

        now = timezone.now()

        # -----------------------------------------------------
        # Active
        # -----------------------------------------------------

        if not coupon.is_active:
            raise ValueError(
                "این کد تخفیف فعال نیست."
            )

        # -----------------------------------------------------
        # Time
        # -----------------------------------------------------

        if now < coupon.start_date:
            raise ValueError(
                "زمان استفاده از این کد تخفیف هنوز شروع نشده است."
            )

        if now > coupon.end_date:
            raise ValueError(
                "زمان استفاده از این کد تخفیف به پایان رسیده است."
            )

        # -----------------------------------------------------
        # Minimum Order
        # -----------------------------------------------------

        if subtotal < coupon.minimum_order_amount:
            raise ValueError(
                f"حداقل مبلغ سفارش برای استفاده از این کد "
                f"{coupon.minimum_order_amount:,} تومان است."
            )

        # -----------------------------------------------------
        # Total Usage Limit
        # -----------------------------------------------------

        if coupon.usage_limit is not None:

            usage_count = CouponUsage.objects.filter(
                coupon=coupon
            ).count()

            if usage_count >= coupon.usage_limit:
                raise ValueError(
                    "ظرفیت استفاده از این کد تخفیف تکمیل شده است."
                )

        # -----------------------------------------------------
        # User Usage Limit
        # -----------------------------------------------------

        user_usage_count = CouponUsage.objects.filter(
            coupon=coupon,
            user=user,
        ).count()

        if user_usage_count >= coupon.usage_limit_per_user:
            raise ValueError(
                "شما قبلاً از این کد تخفیف استفاده کرده‌اید."
            )

        # -----------------------------------------------------
        # Calculate
        # -----------------------------------------------------

        discount = coupon.calculate_discount(
            subtotal
        )

        if discount <= 0:
            raise ValueError(
                "این کد تخفیف برای این سفارش قابل استفاده نیست."
            )

        return coupon, discount

    # =========================================================
    # Shipping
    # =========================================================

    @staticmethod
    def get_shipping_method(shipping_method_id):

        try:

            shipping_method = (
                ShippingMethod.objects.get(
                    id=shipping_method_id,
                    is_active=True,
                )
            )

        except ShippingMethod.DoesNotExist:

            raise ValueError(
                "روش ارسال انتخاب‌شده معتبر نیست."
            )

        return shipping_method

    # =========================================================
    # Address
    # =========================================================

    @staticmethod
    def get_user_address(
        user,
        address_id,
    ):

        try:

            address = Address.objects.get(
                id=address_id,
                user=user,
            )

        except Address.DoesNotExist:

            raise ValueError(
                "آدرس انتخاب‌شده معتبر نیست."
            )

        return address

    # =========================================================
    # Order Number
    # =========================================================

    @staticmethod
    def generate_order_number():
        """
        تولید شماره سفارش یکتا.
        """

        import uuid

        while True:

            order_number = (
                timezone.now().strftime("%Y%m%d")
                + "-"
                + uuid.uuid4().hex[:12].upper()
            )

            if not Order.objects.filter(
                order_number=order_number
            ).exists():

                return order_number

    # =========================================================
    # Create Order
    # =========================================================

    @staticmethod
    @transaction.atomic
    def create_order(
        user,
        address_id,
        shipping_method_id,
        coupon_code=None,
    ):
        """
        ساخت سفارش به صورت Transactional.

        در این مرحله:
        - پروفایل بررسی می‌شود
        - Cart بررسی می‌شود
        - موجودی بررسی می‌شود
        - Address بررسی می‌شود
        - Shipping بررسی می‌شود
        - Coupon بررسی می‌شود
        - Order ساخته می‌شود
        - OrderItem ساخته می‌شود
        - موجودی رزرو/کسر می‌شود
        - Cart خالی می‌شود

        مصرف واقعی Coupon در Payment موفق ثبت خواهد شد.
        """

        # =====================================================
        # Profile
        # =====================================================

        OrderService.validate_profile(
            user
        )

        # =====================================================
        # Lock Cart
        # =====================================================

        cart = (
            Cart.objects
            .select_for_update()
            .get(
                user=user
            )
        )

        # =====================================================
        # Lock Cart Items
        # =====================================================

        items = list(
            CartItem.objects
            .select_for_update()
            .select_related(
                "variant",
                "variant__product",
                "variant__size",
                "variant__color",
            )
            .filter(
                cart=cart
            )
        )

        if not items:

            raise ValueError(
                "سبد خرید شما خالی است."
            )

        # =====================================================
        # Lock Variants
        # =====================================================

        variant_ids = [
            item.variant_id
            for item in items
        ]

        variants = {
            variant.id: variant
            for variant in (
                ProductVariant.objects
                .select_for_update()
                .select_related(
                    "product",
                    "size",
                    "color",
                )
                .filter(
                    id__in=variant_ids
                )
            )
        }

        # =====================================================
        # Validate Stock
        # =====================================================

        for item in items:

            variant = variants.get(
                item.variant_id
            )

            if variant is None:
                raise ValueError(
                    "یکی از محصولات سبد خرید دیگر وجود ندارد."
                )

            if not variant.is_active:
                raise ValueError(
                    f"محصول «{variant.product.title}» دیگر فعال نیست."
                )

            if variant.stock < item.quantity:
                raise ValueError(
                    f"موجودی «{variant.product.title}» کافی نیست."
                )

        # =====================================================
        # Address
        # =====================================================

        address = OrderService.get_user_address(
            user=user,
            address_id=address_id,
        )

        # =====================================================
        # Shipping
        # =====================================================

        shipping_method = (
            OrderService.get_shipping_method(
                shipping_method_id
            )
        )

        # =====================================================
        # Subtotal
        # =====================================================

        subtotal = 0

        for item in items:

            variant = variants[
                item.variant_id
            ]

            subtotal += (
                variant.final_price
                * item.quantity
            )

        # =====================================================
        # Coupon
        # =====================================================

        coupon = None
        coupon_discount = 0

        if coupon_code:

            coupon, coupon_discount = (
                OrderService.validate_coupon(
                    user=user,
                    code=coupon_code,
                    subtotal=subtotal,
                )
            )

        # =====================================================
        # Shipping Cost
        # =====================================================

        amount_after_discount = max(
            subtotal - coupon_discount,
            0,
        )

        shipping_cost = (
            shipping_method.calculate_cost(
                amount_after_discount
            )
        )

        # =====================================================
        # Final Price
        # =====================================================

        total_price = (
            amount_after_discount
            + shipping_cost
        )

        # =====================================================
        # Order
        # =====================================================

        order = Order.objects.create(

            user=user,

            order_number=(
                OrderService.generate_order_number()
            ),

            status=Order.Status.PENDING,

            coupon=coupon,

            coupon_code=(
                coupon.code
                if coupon
                else ""
            ),

            coupon_discount=coupon_discount,

            shipping_method=shipping_method,

            shipping_title=shipping_method.title,

            shipping_cost=shipping_cost,

            # -------------------------------------------------
            # Address Snapshot
            # -------------------------------------------------

            recipient_name=address.recipient_name,

            recipient_phone=address.recipient_phone,

            province=address.province,

            city=address.city,

            address=address.address,

            postal_code=address.postal_code,

            plaque=address.plaque,

            unit=address.unit,

            # -------------------------------------------------
            # Price
            # -------------------------------------------------

            subtotal=subtotal,

            discount_amount=coupon_discount,

            total_price=total_price,
        )

        # =====================================================
        # Order Items + Stock
        # =====================================================

        for item in items:

            variant = variants[
                item.variant_id
            ]

            unit_price = variant.final_price

            item_subtotal = (
                unit_price
                * item.quantity
            )

            OrderItem.objects.create(

                order=order,

                variant=variant,

                # ---------------------------------------------
                # Snapshot
                # ---------------------------------------------

                product_title=(
                    variant.product.title
                ),

                sku=variant.sku,

                size=(
                    variant.size.title
                ),

                color=(
                    variant.color.title
                ),

                color_code=(
                    variant.color.code
                ),

                # ---------------------------------------------
                # Price Snapshot
                # ---------------------------------------------

                original_unit_price=(
                    variant.price
                ),

                discount_percent=(
                    variant.discount_percent
                ),

                unit_price=unit_price,

                quantity=item.quantity,

                subtotal=item_subtotal,
            )

            # ---------------------------------------------
            # Reserve / decrease stock
            # ---------------------------------------------

            variant.stock -= item.quantity

            variant.save(
                update_fields=[
                    "stock",
                    "updated_date",
                ]
            )

        # =====================================================
        # Clear Cart
        # =====================================================

        CartItem.objects.filter(
            cart=cart
        ).delete()

        return order

    # =========================================================
    # Cancel Order
    # =========================================================

    @staticmethod
    @transaction.atomic
    def cancel_order(order):

        order = (
            Order.objects
            .select_for_update()
            .prefetch_related(
                "items"
            )
            .get(
                pk=order.pk
            )
        )

        if order.status != Order.Status.PENDING:

            raise ValueError(
                "فقط سفارش‌های در انتظار پرداخت قابل لغو هستند."
            )

        # =====================================================
        # Return Stock
        # =====================================================

        for item in order.items.all():

            variant = (
                ProductVariant.objects
                .select_for_update()
                .get(
                    pk=item.variant_id
                )
            )

            variant.stock += item.quantity

            variant.save(
                update_fields=[
                    "stock",
                    "updated_date",
                ]
            )

        # =====================================================
        # Cancel
        # =====================================================

        order.status = (
            Order.Status.CANCELLED
        )

        order.cancelled_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_date",
            ]
        )

        return order