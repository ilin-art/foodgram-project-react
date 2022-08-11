from django.contrib import admin
from import_export.admin import ImportMixin
from shop.models import Cart, Item, Product
from shop.resources import CartResource, ItemResource, ProductResource



class ProductAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = ProductResource


class ItemAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = ItemResource


class CartAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = CartResource

admin.site.register(Product, ProductAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Cart, CartAdmin)
