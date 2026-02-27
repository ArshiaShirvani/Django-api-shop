from django.db import models
from accounts.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from shop.models import ProductVariant,Product
from django.utils import timezone
from payment.models import PaymentModel

class OrderStatusType(models.IntegerChoices):
    PENDING = 1,"در انتظار پرداخت"
    SUCCESS = 2,"موفقیت آمیز"
    FAILED = 3,"لغو شده"
    
    
class ShippingMethodType(models.IntegerChoices):
    PISHTAZ = 1,"پست پیشتاز"
    TIPAX = 2,"تیپاکس"
    LOCAL = 3,"ارسال درون اصفهان"
    

class UserAddressModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="کاربر")
    email = models.EmailField(null=True,blank=True,verbose_name="ایمیل")
    address = models.TextField(verbose_name="آدرس")
    state = models.CharField(max_length=100,verbose_name="استان")
    city = models.CharField(max_length=100,verbose_name="شهر")
    zip_code = models.CharField(max_length=30,verbose_name="کد پستی")
    plate = models.CharField(max_length=10,blank=True,null=True,verbose_name="پلاک")
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.user.phone_number
    
    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس ها'
        

class CouponModel(models.Model):
    code = models.CharField(max_length=10,unique=True,verbose_name="کد")
    discount_percent = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(70)],verbose_name="درصد تخفیف")
    allowed_users = models.ManyToManyField(User,blank=True,related_name="coupons",verbose_name="کاربران مجاز برای استفاده")
    used_by = models.ManyToManyField(User,blank=True,related_name="used_coupons",verbose_name="کاربرانی که کد را استفاده کردند")
    expiration_date = models.DateTimeField(verbose_name="تاریخ انقضا")
    
    is_active = models.BooleanField(default=False,verbose_name="فعال")
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کد تخفیف ها'
    
    def __str__(self):
        return self.code
    @property
    def active(self):
        return self.is_active and self.expiration_date > timezone.now()

    def can_use(self, user: User):
        """checking user coupons that user can use it or not"""
        if not self.active:
            return False
        if self.allowed_users.exists() and user not in self.allowed_users.all():
            return False
        if user in self.used_by.all():
            return False
        return True

class OrderModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT,related_name="orders",verbose_name="کاربر")
    address = models.ForeignKey(UserAddressModel,on_delete=models.PROTECT,verbose_name="آدرس")
    total_price = models.DecimalField(max_digits=10,decimal_places=0,default=0,verbose_name="قیمت نهایی")
    
    coupon = models.ForeignKey(CouponModel,on_delete=models.PROTECT,null=True,blank=True,verbose_name="کد تخفیف")
    tax_percent = models.SmallIntegerField(default=10,verbose_name="درصد مالیات")
    shipping_method = models.IntegerField(choices=ShippingMethodType.choices,verbose_name="روش ارسال")
    
    status = models.IntegerField(choices=OrderStatusType.choices, default=OrderStatusType.PENDING,verbose_name="وضعیت")
    payment = models.OneToOneField(
        PaymentModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="order"
    )
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.id}"

    def calculate_total(self):
        """calculate orders with tax and coupon"""
        subtotal = sum(
            item.quantity * item.variant.final_price for item in self.order_items.all()
        )
        discount = 0
        if self.coupon and self.coupon.can_use(self.user):
            discount = subtotal * (self.coupon.discount_percent / 100)
        tax = (subtotal - discount) * (self.tax_percent / 100)
        self.total_price = subtotal - discount + tax
        return self.total_price
    
    
class OrderItemsModel(models.Model):
    order = models.ForeignKey(OrderModel,on_delete=models.CASCADE,related_name="order_items",verbose_name="سفارش")
    variant = models.ForeignKey(ProductVariant,on_delete=models.PROTECT,verbose_name="محصول")
    quantity = models.PositiveIntegerField(default=1,verbose_name="تعداد")
    price = models.DecimalField(max_digits=10,decimal_places=0,default=0,verbose_name="قیمت")
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.variant.product.title
    
    def save(self, *args, **kwargs):
        self.price = self.variant.final_price
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم های سفارش'