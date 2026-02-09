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
        
class ProductSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','slug','description','categories','status']
        
class ProductImageSerilizer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['id','product','image','is_main']
        
class ProductVariantSerilizer(serializers.ModelSerializer):
    size = ProductSizeSerilizer(read_only=True)
    color = ProductColorSerilizer(read_only=True)
    final_price = serializers.IntegerField(source='final_price',read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id','product','size','color','price','final_price','discount_percent','stock','is_active','sku']