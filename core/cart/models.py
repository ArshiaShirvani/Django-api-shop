from django.db import models
from accounts.models import User
from shop.models import ProductVariant

class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart",verbose_name="کاربر")
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.user.phone_number
    
    def total_price(self):
        pass
    
    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد های خرید'
        
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items",verbose_name="سبد خرید")
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name="cart_items",verbose_name="محصول")
    quantity = models.PositiveIntegerField(default=1,verbose_name="تعداد")
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    class Meta:
        unique_together = ('cart', 'variant')
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم های سبد خرید'
        
    
        
    
    @property
    def price(self):
        return self.variant.final_price()

    @property
    def subtotal(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.id} - {self.variant.product.title} - {self.quantity}"
