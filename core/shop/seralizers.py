from rest_framework import serializers
from .models import (
    Product,
    ProductCategory,
    ProductSize,
    ProductColor,
    ProductVariant,
    ProductImages,
    ProductStatus
)

class ProductCategorySerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id','title','slug']
        
        
class ProductSizeSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id','title']
        
        
class ProductColorSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id','title','code']
        
        
class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()           
    original_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()  
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "price",
            "original_price",
            "discount_percent",
            "main_image",
            "created_date",
        ]

    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first()
        if image:
            return image.image.url
        return None

    def get_price(self, obj):
        variant = obj.variants.filter(is_active=True).first()
        if variant:
            return variant.final_price
        return None

    def get_original_price(self, obj):
        variant = obj.variants.filter(is_active=True).first()
        if variant:
            return variant.price
        return None
    
    def get_discount_percent(self, obj):
        variant = obj.variants.filter(is_active=True).first()
        if variant:
            return variant.discount_percent
        return None
        
        
class ProductImageSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['id','product','image','is_main','created_date']
        
        
class ProductVariantSerilizer(serializers.ModelSerializer):
    size = ProductSizeSerilizer(read_only=True)
    color = ProductColorSerilizer(read_only=True)
    final_price = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id','product','size','color','price','final_price','discount_percent','stock','is_active','sku','created_date']
        
        
class ProductDetailSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerilizer(many=True, read_only=True)
    images = ProductImageSerilizer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "images",
            "variants",
            "created_date"
        ]