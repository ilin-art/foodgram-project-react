from django.db.models import F
from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializer
from rest_framework.validators import UniqueTogetherValidator

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
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=IngredientsRecipe.objects.all(),
        #         fields=['ingredient', 'recipe']
        #     )
        # ]


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

        # new_ingredients = [
        #     IngredientsRecipe(
        #         recipe=recipe,
        #         ingredient = get_object_or_404(Ingredient, id=ingredient['ingredient']['id'].id),
        #         amount = ingredient['amount'],
        #     )
        #     for ingredient in ingredients
        # ]
        # IngredientsRecipe.objects.bulk_create(new_ingredients)
        return recipe

    def update(self, instance, validated_data):
        # if 'ingredients' in self.initial_data:
        if 'recipe_content' in validated_data:
            # ingredients = self.context['request'].data['ingredients']
            ingredients = validated_data.pop('recipe_content')
            instance.ingredients.clear()
            self.ingtedient_create(ingredients, instance)
        # if 'tags' in self.initial_data:
        if 'tags' in validated_data:
            # instance.tags.clear()
            # tags = self.context['request'].data['tags']
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        # super().update(instance, validated_data)
        # self.ingtedient_create(instance, ingredients)
        # print(validated_data)
        return super().update(instance, validated_data)

        # instance.name = validated_data.get('name', instance.name)
        # instance.text = validated_data.get('text', instance.text)
        # instance.cooking_time = validated_data.get('cooking_time',
        #                                            instance.cooking_time)
        # instance.image = validated_data.get('image', instance.image)
        # instance.save()
        # return instance

    # def update(self, instance, validated_data):
    #     if 'ingredients' in validated_data:
    #         ingredients = validated_data.pop('recipe_content')
    #         instance.ingredients.clear()
    #         self.ingtedient_create(ingredients, instance)
    #     if 'tags' in validated_data:
    #         tags_data = validated_data.pop('tags')
    #         instance.tags.set(tags_data)
    #     super().update(instance, validated_data)
    #     return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data['recipe_content']
        # ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        # tags = self.initial_data.get('tags')
        tags = data['tags'] 
        tags_set = set()
        # cooking_time = self.initial_data.get('cooking_time')
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
            # id = ingredient.get('id')
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
                # ingredient_id=ingredient.get('id'),
                ingredient_id=ingredient['ingredient'].get('id'),
                # ingredient=ingredient['ingredient'].get('id'),
                amount=ingredient.get('amount')))
        IngredientsRecipe.objects.bulk_create(bulk_list)

    # def ingtedient_create(self, ingredients, recipe):
    #     for ingredient in ingredients:
    #         obj = get_object_or_404(Ingredient, id=ingredient['id'])
    #         amount = ingredient['amount']
    #         if IngredientsRecipe.objects.filter(recipe=recipe,
    #                                             ingredient=obj).exists():
    #             amount += F('amount')
    #         IngredientsRecipe.objects.update_or_create(recipe=recipe,
    #                                                    ingredient=obj,
    #                                                    defaults={'amount': amount})

    # def to_representation(self, instance):
    #     return PostRecipeSerializer(
    #         instance,
    #         context={
    #             'request': self.context.get('request')
    #         }).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField()
    cooking_time = serializers.DecimalField(max_digits=4,
                                            decimal_places=1)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

