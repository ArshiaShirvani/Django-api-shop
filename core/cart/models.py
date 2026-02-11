from django.db import models
from accounts.models import User
from shop.models import ProductVariant

class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.phone_number
    
    def total_price(self):
        pass
        
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'variant')
    
    @property
    def price(self):
        return self.variant.final_price()

    @property
    def subtotal(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.id} - {self.variant.product.title} - {self.quantity}"
