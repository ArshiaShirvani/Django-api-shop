from rest_framework import serializers
from .models import Cart,CartItem



from rest_framework import serializers
from .models import Cart, CartItem
from shop.models import ProductVariant


class AddCartItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        cart = self.context["cart"]

        try:
            variant = ProductVariant.objects.select_related(
                "product", "size", "color"
            ).get(id=data["variant_id"], is_active=True)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("تنوع محصول معتبر نیست")

        try:
            item = CartItem.objects.get(cart=cart, variant=variant)
            new_quantity = item.quantity + data["quantity"]
        except CartItem.DoesNotExist:
            new_quantity = data["quantity"]

        if new_quantity > variant.stock:
            raise serializers.ValidationError("موجودی کافی نیست")

        data["variant"] = variant
        return data



class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="variant.product.title")
    size = serializers.CharField(source="variant.size.title")
    color = serializers.CharField(source="variant.color.title")
    color_code = serializers.CharField(source="variant.color.code")
    price = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "variant",
            "product_title",
            "size",
            "color",
            "color_code",
            "price",
            "quantity",
            "subtotal",
            "image",
        ]

    def get_price(self, obj):
        return obj.variant.final_price()

    def get_subtotal(self, obj):
        return obj.variant.final_price() * obj.quantity

    def get_image(self, obj):
        img = obj.variant.product.images.filter(is_main=True).first()
        return img.image.url if img else None



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]
