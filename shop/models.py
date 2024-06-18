from tabnanny import verbose
from django.db import models
from account.models import User
from vendor.models import Vendor
from django.core.exceptions import ValidationError


class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def clean(self):
        self.category_name = self.category_name.capitalize()
    
    def __str__(self):
        return self.category_name



class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fooditems')
    product_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images')
    
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_title


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        user = self.user
        if not user.is_verified:
            raise ValidationError("User must be verified to invest")
        
        max_shares_per_user = self.project.max_shares_per_user
        total_shares = self.project.total_no_shares

        # Check if the quantity exceeds the maximum shares per user
        if self.quantity > max_shares_per_user:
            raise ValidationError("Quantity exceeds the maximum shares per user")

        # Check if the quantity exceeds the available shares
        if self.quantity > total_shares:
            raise ValidationError("No more shares available")

        existing_cart = Cart.objects.filter(user=user).exclude(pk=self.pk).first()
        if existing_cart:
            raise ValidationError("Only one project is allowed per user in the cart.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)

class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'tax'

    def __str__(self):
        return self.tax_type