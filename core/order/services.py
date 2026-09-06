import uuid

from django.core.exceptions import ValidationError
from django.db import transaction

from cart.models import Cart
from shop.models import ProductVariant

from .models import (
    Address,
    ShippingMethod,
    Coupon,
    CouponUsage,
    Order,
    OrderItem,
    OrderStatus,
)


class OrderService:

    TAX_PERCENT = 10

    # =========================================================
    # CREATE ORDER
    # =========================================================

    @staticmethod
    @transaction.atomic
    def create_order(
        *,
        user,
        address,
        shipping_method,
        coupon=None,
    ):
        """
        ساخت سفارش از روی سبد خرید.

        این متد:
        - Cart را بررسی می‌کند
        - موجودی را بررسی می‌کند
        - قیمت‌ها را Snapshot می‌کند
        - تخفیف را محاسبه می‌کند
        - مالیات را محاسبه می‌کند
        - هزینه ارسال را محاسبه می‌کند
        - Order و OrderItem ایجاد می‌کند

        در این مرحله:
        - stock کم نمی‌شود
        - cart خالی نمی‌شود
        - coupon مصرف نمی‌شود
        - tracking code ساخته نمی‌شود

        سفارش در وضعیت PENDING ایجاد می‌شود.
        """

        # =====================================================
        # 1. USER
        # =====================================================

        if not user or not user.is_authenticated:
            raise ValidationError(
                "کاربر احراز هویت نشده است."
            )

        # =====================================================
        # 2. PROFILE
        # =====================================================

        profile = getattr(
            user,
            "profile",
            None,
        )

        if not profile:
            raise ValidationError(
                "پروفایل کاربر وجود ندارد."
            )

        if not profile.first_name or not profile.last_name:
            raise ValidationError(
                "ابتدا نام و نام خانوادگی خود را تکمیل کنید."
            )

        # =====================================================
        # 3. ADDRESS
        # =====================================================

        if not address:
            raise ValidationError(
                "انتخاب آدرس الزامی است."
            )

        if address.user_id != user.id:
            raise ValidationError(
                "این آدرس متعلق به شما نیست."
            )

        # =====================================================
        # 4. SHIPPING METHOD
        # =====================================================

        if not shipping_method:
            raise ValidationError(
                "انتخاب روش ارسال الزامی است."
            )

        if not shipping_method.is_active:
            raise ValidationError(
                "این روش ارسال در حال حاضر فعال نیست."
            )

        # =====================================================
        # 5. LOCK CART
        # =====================================================

        try:

            cart = (
                Cart.objects
                .select_for_update()
                .get(
                    user=user
                )
            )

        except Cart.DoesNotExist:

            raise ValidationError(
                "سبد خرید شما وجود ندارد."
            )

        # =====================================================
        # 6. CART ITEMS
        # =====================================================

        cart_items = list(
            cart.items.select_related(
                "variant",
                "variant__product",
                "variant__size",
                "variant__color",
            )
        )

        if not cart_items:
            raise ValidationError(
                "سبد خرید شما خالی است."
            )

        # =====================================================
        # 7. LOCK VARIANTS
        # =====================================================

        variant_ids = [
            item.variant_id
            for item in cart_items
        ]

        locked_variants = {
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
        # 8. VALIDATE STOCK
        # =====================================================

        for cart_item in cart_items:

            variant = locked_variants.get(
                cart_item.variant_id
            )

            if not variant:

                raise ValidationError(
                    f"محصول «{cart_item.variant.product.title}» "
                    "دیگر وجود ندارد."
                )

            if not variant.is_active:

                raise ValidationError(
                    f"محصول «{variant.product.title}» "
                    "دیگر فعال نیست."
                )

            if variant.stock < cart_item.quantity:

                raise ValidationError(
                    f"موجودی محصول «{variant.product.title}» "
                    "برای تعداد انتخاب‌شده کافی نیست."
                )

        # =====================================================
        # 9. CALCULATE SUBTOTAL
        # =====================================================

        subtotal = 0

        for cart_item in cart_items:

            variant = locked_variants[
                cart_item.variant_id
            ]

            subtotal += (
                variant.final_price
                * cart_item.quantity
            )

        # =====================================================
        # 10. COUPON
        # =====================================================

        discount = 0

        if coupon:

            if not coupon.is_available_for_user(
                user
            ):
                raise ValidationError(
                    "این کد تخفیف برای شما قابل استفاده نیست."
                )

            discount = coupon.calculate_discount(
                subtotal
            )

            if discount <= 0:

                raise ValidationError(
                    "این کد تخفیف روی مبلغ سفارش قابل اعمال نیست."
                )

        # =====================================================
        # 11. TAXABLE AMOUNT
        # =====================================================

        taxable_amount = max(
            subtotal - discount,
            0
        )

        # =====================================================
        # 12. SHIPPING COST
        # =====================================================

        shipping_cost = (
            shipping_method.calculate_cost(
                taxable_amount
            )
        )

        # =====================================================
        # 13. TAX
        # =====================================================

        tax = (
            taxable_amount
            * OrderService.TAX_PERCENT
        ) // 100

        # =====================================================
        # 14. TOTAL
        # =====================================================

        total = (
            taxable_amount
            + tax
            + shipping_cost
        )

        # =====================================================
        # 15. CREATE ORDER
        # =====================================================

        order_data = {
            "user": user,

            "status": OrderStatus.PENDING,

            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "shipping_cost": shipping_cost,
            "total": total,

            "coupon": coupon,

            "shipping_method": shipping_method,

            # Address snapshot
            "recipient_name": address.recipient_name,
            "recipient_phone": address.recipient_phone,
            "province": address.province,
            "city": address.city,
            "address": address.address,
            "postal_code": address.postal_code,
            "plaque": address.plaque,
            "unit": address.unit,
        }

        # اگر coupon_code در مدل Order اضافه شده باشد
        if hasattr(Order, "coupon_code"):
            order_data["coupon_code"] = (
                coupon.code
                if coupon
                else ""
            )

        order = Order.objects.create(
            **order_data
        )

        # =====================================================
        # 16. CREATE ORDER ITEMS
        # =====================================================

        order_items = []

        for cart_item in cart_items:

            variant = locked_variants[
                cart_item.variant_id
            ]

            unit_price = variant.final_price

            order_items.append(
                OrderItem(
                    order=order,

                    variant=variant,

                    # -----------------------------
                    # Product snapshot
                    # -----------------------------

                    product_title=(
                        variant.product.title
                    ),

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

                    sku=variant.sku,

                    # -----------------------------
                    # Price snapshot
                    # -----------------------------

                    unit_price=unit_price,

                    quantity=cart_item.quantity,

                    subtotal=(
                        unit_price
                        * cart_item.quantity
                    ),
                )
            )

        OrderItem.objects.bulk_create(
            order_items
        )

        return order

    # =========================================================
    # FINALIZE ORDER
    # =========================================================

    @staticmethod
    @transaction.atomic
    def finalize_order(
        *,
        order_id,
    ):
        """
        نهایی کردن سفارش بعد از پرداخت موفق.

        این متد باید فقط بعد از تأیید موفق Payment اجرا شود.

        عملیات:
        1. Lock Order
        2. بررسی وضعیت
        3. Lock ProductVariants
        4. بررسی موجودی
        5. Lock Coupon
        6. ثبت CouponUsage
        7. کاهش Stock
        8. حذف/کاهش آیتم‌های Cart
        9. ساخت Tracking Code
        10. تغییر وضعیت Order به PAID
        """

        # =====================================================
        # 1. LOCK ORDER
        # =====================================================

        try:

            order = (
                Order.objects
                .select_for_update()
                .select_related(
                    "user",
                    "coupon",
                    "shipping_method",
                )
                .get(
                    id=order_id
                )
            )

        except Order.DoesNotExist:

            raise ValidationError(
                "سفارش مورد نظر پیدا نشد."
            )

        # =====================================================
        # 2. IDEMPOTENCY
        # =====================================================

        if order.status == OrderStatus.PAID:

            return order

        if order.status != OrderStatus.PENDING:

            raise ValidationError(
                "این سفارش قابل نهایی شدن نیست."
            )

        # =====================================================
        # 3. ORDER ITEMS
        # =====================================================

        order_items = list(
            OrderItem.objects
            .filter(
                order=order
            )
        )

        if not order_items:

            raise ValidationError(
                "این سفارش هیچ آیتمی ندارد."
            )

        # =====================================================
        # 4. LOCK VARIANTS
        # =====================================================

        variant_ids = [
            item.variant_id
            for item in order_items
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
        # 5. VALIDATE VARIANTS / STOCK
        # =====================================================

        for item in order_items:

            variant = variants.get(
                item.variant_id
            )

            if not variant:

                raise ValidationError(
                    f"محصول «{item.product_title}» "
                    "دیگر وجود ندارد."
                )

            if not variant.is_active:

                raise ValidationError(
                    f"محصول «{item.product_title}» "
                    "دیگر فعال نیست."
                )

            if variant.stock < item.quantity:

                raise ValidationError(
                    f"موجودی محصول «{item.product_title}» "
                    "برای تکمیل سفارش کافی نیست."
                )

        # =====================================================
        # 6. LOCK COUPON
        # =====================================================

        coupon = None

        if order.coupon_id:

            coupon = (
                Coupon.objects
                .select_for_update()
                .get(
                    id=order.coupon_id
                )
            )

            # ---------------------------------------------
            # Active
            # ---------------------------------------------

            if not coupon.is_active:

                raise ValidationError(
                    "کد تخفیف دیگر فعال نیست."
                )

            # ---------------------------------------------
            # Time
            # ---------------------------------------------

            if not coupon.is_valid_time:

                raise ValidationError(
                    "اعتبار زمانی کد تخفیف به پایان رسیده است."
                )

            # ---------------------------------------------
            # User access
            # ---------------------------------------------

            if (
                not coupon.is_global
                and not coupon.users.filter(
                    id=order.user_id
                ).exists()
            ):

                raise ValidationError(
                    "این کد تخفیف برای این کاربر قابل استفاده نیست."
                )

            # ---------------------------------------------
            # Global usage limit
            # ---------------------------------------------

            if coupon.usage_limit is not None:

                total_usage = (
                    CouponUsage.objects
                    .filter(
                        coupon=coupon
                    )
                    .count()
                )

                if total_usage >= coupon.usage_limit:

                    raise ValidationError(
                        "ظرفیت استفاده از این کد تخفیف تکمیل شده است."
                    )

            # ---------------------------------------------
            # User usage limit
            # ---------------------------------------------

            user_usage = (
                CouponUsage.objects
                .filter(
                    coupon=coupon,
                    user_id=order.user_id,
                )
                .count()
            )

            if (
                coupon.usage_limit_per_user is not None
                and
                user_usage >= coupon.usage_limit_per_user
            ):

                raise ValidationError(
                    "شما قبلاً به حداکثر میزان مجاز "
                    "از این کد تخفیف استفاده کرده‌اید."
                )

        # =====================================================
        # 7. DECREASE STOCK
        # =====================================================

        for item in order_items:

            variant = variants[
                item.variant_id
            ]

            variant.stock -= item.quantity

            variant.save(
                update_fields=[
                    "stock",
                ]
            )

        # =====================================================
        # 8. CREATE COUPON USAGE
        # =====================================================

        if coupon:

            CouponUsage.objects.create(
                coupon=coupon,
                user=order.user,
                order=order,
            )

        # =====================================================
        # 9. CLEAR / UPDATE CART
        # =====================================================

        try:

            cart = (
                Cart.objects
                .select_for_update()
                .get(
                    user=order.user
                )
            )

            for item in order_items:

                try:

                    cart_item = (
                        cart.items
                        .select_for_update()
                        .get(
                            variant_id=item.variant_id
                        )
                    )

                except cart.items.model.DoesNotExist:

                    continue

                # اگر کاربر بعد از ساخت Order
                # همان محصول را دوباره به Cart اضافه کرده
                # باشد، فقط مقدار مربوط به این Order
                # را کم می‌کنیم.

                if cart_item.quantity <= item.quantity:

                    cart_item.delete()

                else:

                    cart_item.quantity -= item.quantity

                    cart_item.save(
                        update_fields=[
                            "quantity",
                            "updated_date",
                        ]
                    )

        except Cart.DoesNotExist:

            pass

        # =====================================================
        # 10. TRACKING CODE
        # =====================================================

        tracking_code = (
            OrderService.generate_tracking_code()
        )

        order.tracking_code = tracking_code

        # =====================================================
        # 11. CHANGE ORDER STATUS
        # =====================================================

        order.status = OrderStatus.PAID

        order.save(
            update_fields=[
                "tracking_code",
                "status",
                "updated_date",
            ]
        )

        return order

    # =========================================================
    # GENERATE TRACKING CODE
    # =========================================================

    @staticmethod
    def generate_tracking_code():
        """
        ساخت Tracking Code یکتا.
        """

        while True:

            tracking_code = (
                "ORD-"
                + uuid.uuid4().hex[:12].upper()
            )

            if not Order.objects.filter(
                tracking_code=tracking_code
            ).exists():

                return tracking_code