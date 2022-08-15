from django_filters import filters
from django_filters.rest_framework import FilterSet

from .models import Product


class ProductFilter(FilterSet):
    author = filters.AllValuesFilter(field_name='author')
    item = filters.AllValuesMultipleFilter(field_name='item__slug')

    class Meta:
        model = Product
        fields = ['author', 'item']
