from django.db import models



class ProductStatus(models.IntegerChoices):
    PUBLISHED = 1, "فعال"
    DRAFT = 2, "غیر فعال"
    
    
class ProductCategory(models.Model):
    title = models.CharField(max_length=200, unique=True,verbose_name='عنوان دسته بندی')
    slug = models.SlugField(max_length=200, unique=True,allow_unicode=True,verbose_name='اسلاگ دسته بندی')
    image = models.ImageField(upload_to='shop/categories/images/',verbose_name='عکس',null=True,blank=True)
    
    parent = models.ForeignKey("self",on_delete=models.CASCADE,null=True,blank=True,related_name="children")
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'دسته بندی محصول'
        verbose_name_plural = 'دسته بندی محصولات'
    
    @property
    def is_root(self):
        return self.parent is None

class Feature(models.Model):
    title = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی ها'
        
    def __str__(self):
        return self.title
        
    
class Product(models.Model):
    title = models.CharField(max_length=200, unique=True,verbose_name='عنوان محصول')
    slug = models.SlugField(max_length=200, unique=True,allow_unicode=True,verbose_name='اسلاگ محصول')
    description = models.TextField(verbose_name='توضیحات محصول')
    categories = models.ManyToManyField(ProductCategory,verbose_name='دسته بندی ها')
    status = models.IntegerField(choices=ProductStatus.choices,default=ProductStatus.DRAFT.value,verbose_name='وضعیت محصول')
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        

class ProductSize(models.Model):
    title = models.CharField(max_length=10,unique=True,verbose_name='عنوان')
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'سایز محصول'
        verbose_name_plural = 'سایز محصولات'
    
    
class ProductColor(models.Model):
    title = models.CharField(max_length=50,unique=True,verbose_name='عنوان')
    code = models.CharField(max_length=10,unique=True,verbose_name='کد رنگ')
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'رنگ محصول'
        verbose_name_plural = 'رنگ محصولات'
        
    
class ProductImages(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images',verbose_name='محصول')
    image = models.ImageField(upload_to='shop/products/images/',verbose_name='عکس محصول')
    is_main = models.BooleanField(default=False,verbose_name='عکس اصلی')
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'عکس محصول'
        verbose_name_plural = 'عکس محصولات'
        
    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImages.objects.filter(product=self.product, is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.product.title
    
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='variants',verbose_name='محصول')
    
    size = models.ForeignKey(ProductSize,on_delete=models.PROTECT,verbose_name='سایز')
    color = models.ForeignKey(ProductColor,on_delete=models.PROTECT,verbose_name='رنگ')
    
    price = models.IntegerField(verbose_name='قیمت اصلی')
    discount_percent = models.PositiveIntegerField(default=0,verbose_name='درصد تخفیف')
    
    stock = models.PositiveIntegerField(default=0,verbose_name='موجودی انبار')
    is_active = models.BooleanField(default=True,verbose_name='فعال')
    
    sku = models.CharField(max_length=50, unique=True,verbose_name='کد انبار')
    
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروزرسانی')
    
    
    class Meta:
        verbose_name = 'تنوع محصول'
        verbose_name_plural = 'تنوع محصولات'
        
    def save(self, *args, **kwargs):
       
        if ProductVariant.objects.filter(product=self.product, size=self.size, color=self.color).exclude(pk=self.pk).exists():
            raise ValueError("این ترکیب محصول، سایز و رنگ قبلاً ثبت شده است")
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        price = self.price or 0
        discount = self.discount_percent or 0
        return price * (100 - discount) // 100
    
    def __str__(self):
        return f"{self.product.title} - {self.size.title} - {self.color.title}"
    
    
class FeatureValue(models.Model):
    product = models.ForeignKey(Product,related_name="feature_values",on_delete=models.CASCADE,verbose_name="محصول")
    feature = models.ForeignKey(Feature,on_delete=models.PROTECT,verbose_name="ویژگی")
    value = models.CharField(max_length=255,verbose_name="مقدار")
    
    class Meta:
        verbose_name = 'مقدار ویژگی محصول'
        verbose_name_plural = 'مقادیر ویژگی محصولات'
        
    
    def __str__(self):
        return self.product.title