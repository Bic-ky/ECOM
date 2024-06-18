from django.contrib import admin
from .models import Payment, Order, ProductOrder


admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(ProductOrder)