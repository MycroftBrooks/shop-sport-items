from django.contrib import admin

from .models import Order, OrderItem, catalog

admin.site.register(catalog)
admin.site.register(OrderItem)
admin.site.register(Order)
