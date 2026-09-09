from rest_framework import serializers

from accounts.models import Profile

from order.models import Address, Order

from shop.models import Product

from .models import Favorite


# =========================================================
# PROFILE
# =========================================================

class DashboardProfileSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True,
    )

    class Meta:
        model = Profile

        fields = (
            "phone_number",
            "role",
            "first_name",
            "last_name",
        )

        read_only_fields = (
            "phone_number",
            "role",
        )

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام نمی‌تواند خالی باشد."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام خانوادگی نمی‌تواند خالی باشد."
            )

        return value


# =========================================================
# ADDRESS
# =========================================================

class DashboardAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = (
            "id",
            "title",
            "recipient_name",
            "recipient_phone",
            "province",
            "city",
            "address",
            "postal_code",
            "plaque",
            "unit",
            "is_default",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
        )

    def validate(self, attrs):

        recipient_name = attrs.get(
            "recipient_name",
            getattr(
                self.instance,
                "recipient_name",
                None,
            ),
        )

        recipient_phone = attrs.get(
            "recipient_phone",
            getattr(
                self.instance,
                "recipient_phone",
                None,
            ),
        )

        if not recipient_name:
            raise serializers.ValidationError({
                "recipient_name": "نام گیرنده الزامی است."
            })

        if not recipient_phone:
            raise serializers.ValidationError({
                "recipient_phone": "شماره تماس گیرنده الزامی است."
            })

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        return Address.objects.create(
            user=request.user,
            **validated_data,
        )


# =========================================================
# ORDER
# =========================================================

class DashboardOrderSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()

    shipping_method_title = serializers.CharField(
        source="shipping_method.title",
        read_only=True,
    )

    coupon_code_display = serializers.CharField(
        source="coupon.code",
        read_only=True,
    )

    payable_amount = serializers.IntegerField(
        read_only=True,
    )

    is_paid = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Order

        fields = (
            "id",
            "tracking_code",
            "status",

            "subtotal",
            "discount",
            "tax",
            "shipping_cost",
            "total",
            "payable_amount",

            "coupon_code_display",

            "shipping_method",
            "shipping_method_title",

            "recipient_name",
            "recipient_phone",
            "province",
            "city",
            "address",
            "postal_code",
            "plaque",
            "unit",

            "items",

            "is_paid",

            "created_date",
            "updated_date",
        )

        read_only_fields = fields

    def get_items(self, obj):

        from order.serializers import OrderItemSerializer

        return OrderItemSerializer(
            obj.items.all(),
            many=True,
            context=self.context,
        ).data




# =========================================================
# FAVORITE PRODUCT
# =========================================================

class FavoriteProductSerializer(serializers.ModelSerializer):

    main_image = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = (
            "id",
            "title",
            "slug",
            "main_image",
            "price",
        )

    def get_main_image(self, obj):

        image = obj.main_image

        if image:
            request = self.context.get("request")

            if request:
                return request.build_absolute_uri(
                    image.image.url
                )

            return image.image.url

        return None

    def get_price(self, obj):

        variant = (
            obj.variants
            .filter(
                is_active=True,
                stock__gt=0,
            )
            .order_by("price")
            .first()
        )

        if not variant:
            return None

        return variant.final_price


class FavoriteSerializer(serializers.ModelSerializer):

    product = FavoriteProductSerializer(
        read_only=True
    )

    class Meta:
        model = Favorite

        fields = (
            "id",
            "product",
            "created_date",
        )

        read_only_fields = fields


# =========================================================
# FAVORITE CREATE
# =========================================================

class FavoriteCreateSerializer(serializers.Serializer):

    product_id = serializers.IntegerField(
        help_text="شناسه محصول"
    )

    def validate_product_id(self, value):

        try:
            product = Product.objects.get(
                id=value
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "محصول مورد نظر پیدا نشد."
            )

        if product.status != 1:
            raise serializers.ValidationError(
                "این محصول در حال حاضر قابل افزودن به علاقه‌مندی نیست."
            )

        request = self.context.get("request")

        if Favorite.objects.filter(
            user=request.user,
            product=product
        ).exists():
            raise serializers.ValidationError(
                "این محصول قبلاً به علاقه‌مندی‌ها اضافه شده است."
            )

        return value