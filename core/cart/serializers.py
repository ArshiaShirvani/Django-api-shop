from rest_framework import serializers

from .models import Cart, CartItem
from shop.models import ProductVariant


class AddCartItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(
        min_value=1
    )

    quantity = serializers.IntegerField(
        min_value=1
    )

    def validate_variant_id(self, value):
        if not ProductVariant.objects.filter(
            id=value,
            is_active=True,
            stock__gt=0,
        ).exists():
            raise serializers.ValidationError(
                "این تنوع محصول موجود یا فعال نیست."
            )

        return value

    def validate(self, attrs):
        cart = self.context["cart"]

        variant = (
            ProductVariant.objects
            .select_related(
                "product",
                "size",
                "color",
            )
            .get(
                id=attrs["variant_id"],
                is_active=True,
            )
        )

        current_item = (
            CartItem.objects
            .filter(
                cart=cart,
                variant=variant,
            )
            .first()
        )

        current_quantity = (
            current_item.quantity
            if current_item
            else 0
        )

        requested_quantity = attrs["quantity"]

        if current_quantity + requested_quantity > variant.stock:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"حداکثر تعداد قابل افزودن "
                        f"{variant.stock - current_quantity} عدد است."
                    )
                }
            )

        attrs["variant"] = variant
        attrs["current_item"] = current_item

        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1
    )

    def validate(self, attrs):
        item = self.context["item"]

        variant = (
            ProductVariant.objects
            .select_related(
                "product",
                "size",
                "color",
            )
            .get(pk=item.variant_id)
        )

        if not variant.is_active:
            raise serializers.ValidationError(
                "این محصول دیگر فعال نیست."
            )

        if variant.stock <= 0:
            raise serializers.ValidationError(
                "این محصول در حال حاضر موجود نیست."
            )

        if attrs["quantity"] > variant.stock:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        f"حداکثر تعداد قابل انتخاب "
                        f"{variant.stock} عدد است."
                    )
                }
            )

        attrs["variant"] = variant

        return attrs


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="variant.product.title",
        read_only=True,
    )
    
    product_slug = serializers.CharField(
        source="variant.product.slug",
        read_only=True
    )

    product_id = serializers.IntegerField(
        source="variant.product.id",
        read_only=True,
    )

    size = serializers.CharField(
        source="variant.size.title",
        read_only=True,
    )

    color = serializers.CharField(
        source="variant.color.title",
        read_only=True,
    )

    color_code = serializers.CharField(
        source="variant.color.code",
        read_only=True,
    )

    price = serializers.IntegerField(
        source="variant.price",
        read_only=True,
    )

    discount_percent = serializers.IntegerField(
        source="variant.discount_percent",
        read_only=True,
    )

    final_price = serializers.IntegerField(
        source="variant.final_price",
        read_only=True,
    )

    stock = serializers.IntegerField(
        source="variant.stock",
        read_only=True,
    )

    subtotal = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField()

    is_available = serializers.SerializerMethodField()

    class Meta:
        model = CartItem

        fields = [
            "id",
            "variant",
            "product_id",
            "product_title",
            "product_slug",
            "image",
            "size",
            "color",
            "color_code",
            "price",
            "discount_percent",
            "final_price",
            "stock",
            "quantity",
            "subtotal",
            "is_available",
        ]

    def get_subtotal(self, obj):
        return obj.variant.final_price * obj.quantity

    def get_image(self, obj):
        image = obj.variant.product.images.filter(
            is_main=True
        ).first()

        if not image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                image.image.url
            )

        return image.image.url

    def get_is_available(self, obj):
        return (
            obj.variant.is_active
            and obj.variant.stock > 0
            and obj.quantity <= obj.variant.stock
        )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )

    total_price = serializers.SerializerMethodField()

    total_quantity = serializers.SerializerMethodField()

    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart

        fields = [
            "id",
            "items",
            "items_count",
            "total_quantity",
            "total_price",
        ]

    def get_total_price(self, obj):
        return sum(
            item.variant.final_price * item.quantity
            for item in obj.items.all()
        )

    def get_total_quantity(self, obj):
        return sum(
            item.quantity
            for item in obj.items.all()
        )

    def get_items_count(self, obj):
        return len(obj.items.all())