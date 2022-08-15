from import_export import resources

from .models import Cart, Item, Product


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id',
                  'name',
                  'text',
                  'item',
                  'price',)

class ItemResource(resources.ModelResource):
    class Meta:
        model = Item
        fields = ('id', 'HEX_code', 'slug',)


class CartResource(resources.ModelResource):
    class Meta:
        model = Cart
        fields = ('user', 'product',)
