from django.contrib import admin
from .models import Contact, Product, Order, OrderUpdates
# Register your models here.


admin.site.register(Contact)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderUpdates)