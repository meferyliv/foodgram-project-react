from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class SimplifyRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор используется в FollowSerializer для  получения
    краткого отображения сведений о рецептах пользователей,
    на которых подписан текущий пользователь.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций с тегами.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций с ингредиентами.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций с колличеством ингредиентов.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций с рецептами
    """
    tags = TagSerializer(read_only=True, many=True,)
    author = CustomUserSerializer(read_only=True,)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(carts__user=user, id=obj.id).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients_data:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientAmount.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop('ingredients')
        for ingredient in ingredients_data:
            IngredientAmount.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
        instance.save()
        return instance

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужно добавить хотя бы один тэг для рецепта'}
            )
        tags_list = []
        for item in tags:
            tag = get_object_or_404(
                Tag, id=item
            )
            if tag in tags_list:
                raise serializers.ValidationError(
                    {'tags': 'Теги для рецепта не могут повторяться'}
                )
            tags_list.append(tag)
        data['tags'] = tags
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Не может быть рецепта без ингрединтов.'}
            )
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=item['id']
            )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты для рецепта не могут повторяться.'
                )
            if int(item['amount']) < 1:
                raise serializers.ValidationError(
                    'Колличество ингридиента не может быть менее 1.'
                )
            ingredients_list.append(ingredient)
        data['ingredients'] = ingredients
        return data

    def get_ingredients(self, obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций со списком покупок.
    """
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

        def to_representation(self, instance):
            request = self.context.get('request')
            context = {'request': request}
            return SimplifyRecipeSerializer(
                instance=instance.recipe, context=context
            ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций со списком избранного.
    """
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        def to_representation(self, instance):
            request = self.context.get('request')
            context = {'request': request}
            return SimplifyRecipeSerializer(
                instance=instance.recipe, context=context
            ).data
