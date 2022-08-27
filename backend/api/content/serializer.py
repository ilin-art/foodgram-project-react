from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import (Favourite, Ingredient, IngredientsRecipe, Recipe,
                     Shopping, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class AddIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            queryset=Ingredient.objects.all())
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
                                        read_only=True,
                                        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount', )
        model = IngredientsRecipe


class IngredientsEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag

class GetRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author = UserSerializer()
    name = serializers.CharField(read_only=True)
    ingredients = AddIngredientsSerializer(source='recipe_content', 
                                           many=True,
                                           read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField('check_is_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField('check_is_in_shopping')

    def check_is_favorite(self, obj):
        user = self.context.get('request').user.id
        return Favourite.objects.filter(user=user, recipe=obj).exists()

    def check_is_in_shopping(self, obj):
        user = self.context.get('request').user.id
        return Shopping.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')


class PostRecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientsSerializer(source='recipe_content',
                                           many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time',)

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_content')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingtedient_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'recipe_content' in validated_data:
            ingredients = validated_data.pop('recipe_content')
            instance.ingredients.clear()
            self.ingtedient_create(ingredients, instance)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data['recipe_content']
        ingredients_set = set()
        tags = data['tags'] 
        tags_set = set()
        cooking_time = data['cooking_time']
        if not ingredients:
            raise serializers.ValidationError('Выберите ингредиенты')
        if not tags:
            raise serializers.ValidationError(
                'Выберите минимум один тег'
            )
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                    'Значение времени должно быть положительным'
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                        'Значение колво ингредиента должно быть положительным')
            id = ingredient['ingredient'].get('id')
            if id in ingredients_set:
                raise serializers.ValidationError('Ингредиент уже добавлен')
            ingredients_set.add(id)
        for tag in tags:
            if tag in tags_set:
                raise serializers.ValidationError('Этот тэг уже выбран')
            tags_set.add(tag)
        return data

    def ingtedient_create(self, ingredients, recipe):
        bulk_list = list()
        for ingredient in ingredients:
            bulk_list.append(IngredientsRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'].get('id'),
                amount=ingredient.get('amount')))
        IngredientsRecipe.objects.bulk_create(bulk_list)


class ShortRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField()
    cooking_time = serializers.DecimalField(max_digits=4,
                                            decimal_places=1)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
