from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import ProductFilter
from .models import Item, Product
from .serializer import GetProductSerializer, ItemSerializer


class ItemViewSet(ReadOnlyModelViewSet):
    pass
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class ProductViewSet(viewsets.ModelViewSet):
    pass
    queryset = Product.objects.all()
    serializer_class = GetProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination
    filter_class = ProductFilter
