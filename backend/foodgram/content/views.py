from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.colors import black, blue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import RecipeFilter, IngredientSearchFilter
from .models import (Favourite, Ingredient, IngredientsRecipe, Recipe,
                     Shopping, Tag)
from .paginators import CustomPageNumberPaginator
from .serializer import (GetRecipeSerializer, IngredientSerializer,
                         PostRecipeSerializer, ShortRecipeSerializer,
                         TagsSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPageNumberPaginator
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return PostRecipeSerializer

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'GET':
            return self.add_obj(Shopping, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(Shopping, request.user, pk)
        return None

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'GET':
            return self.add_obj(Favourite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(Favourite, request.user, pk)
        return None

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, pk=None):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping.pdf"'
        p = canvas.Canvas(response)
        pdfmetrics.registerFont(TTFont('DejaVuSans','DejaVuSans.ttf', 'UTF-8'))

        res = []
        name = []

        rec_names = (
                Recipe.objects.values(
                    'name',
                )
                .filter(shoppings__user=request.user)
            )
        for item in rec_names:
            name.append(
                f"{item['name'].capitalize()}"
            )
        
        rec_ingredients = (
                IngredientsRecipe.objects.values(
                    'ingredient__name',
                    'ingredient__measurement_unit',
                )
                .filter(recipe__shoppings__user=request.user)
                .annotate(Sum('amount'))
            )
        for rec_ingredient in rec_ingredients:
            res.append(
                f"{rec_ingredient['ingredient__name'].capitalize()} - "
                f"{rec_ingredient['amount__sum']} "
                f"{rec_ingredient['ingredient__measurement_unit']}"
            )

        line_position = 800
        title = f"Список на сегодня:"
        p.setFont("DejaVuSans", 25)
        p.setFillColor(blue)
        p.drawString(30, line_position, title)

        p.setFillColor(blue)
        line_position -= 10
        p.line(30, line_position, 500, line_position)
        
        p.setFillColor(black)
        title = f"Список рецептов:"
        p.setFont("DejaVuSans", 17)
        line_position -= 40
        p.drawString(30, line_position, title)
        title = f"Список инградиентов:"
        p.drawString(300, line_position, title)

        p.setFillColor(blue)
        line_position -= 10
        p.line(30, line_position, 230, line_position)
        p.line(300, line_position, 500, line_position)


        p.setFillColor(black)
        p.setFont("DejaVuSans", 15)
        line_position -= 10

        line_position_ = line_position
        for name_item in name:
            data = str(name_item)
            line_position_ -= 22
            p.drawString(40, line_position_, data)

        p.setFont("DejaVuSans", 15)
        for recipes_item in res:
            data = str(recipes_item)
            line_position -= 22
            p.drawString(310, line_position, data)
        
        p.showPage()
        p.save()
        return response


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
