from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from recipes.models import (
    Recipe,
    Ingredient,
    IngredientRecipe,
    ShoppingCart,
    Favorite,
    Follow,
)
from users.serializers import UserSerializer
from http import HTTPStatus

MIN_AMOUNT = 1
MAX_AMOUNT = 32000
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000

class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer для Подписок."""

    name = serializers.ReadOnlyField(source="recipe.name", read_only=True)
    image = serializers.ImageField(source="recipe.image", read_only=True)
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(source="recipe", read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer для Корзины."""

    name = serializers.ReadOnlyField(source="recipe.name", read_only=True)
    image = serializers.ImageField(source="recipe.image", read_only=True)
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(source="recipe", read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id",)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Serializer для рецептов и ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer для Рецептов.
    """

    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True, source="recipe_ingredients", read_only=True
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj) -> bool:
        request = self.context["request"]
        return request.user.is_authenticated and obj.favorite.filter(
            user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        return (request.user.is_authenticated
            and obj.shopping_cart.filter(author=request.user).exists())


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer для поля ingredient модели Recipe - создание ингредиентов.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT, max_value=MAX_AMOUNT)

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer для модели Recipe - запись / обновление / удаление данных."""

    ingredients = AddIngredientSerializer(many=True, write_only=True)
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME, max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def validate(self, data):
        """Валидация перед созданием/обновлением рецепта"""
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно"},
                code='required'
            )
        if 'image' not in data:
            raise serializers.ValidationError(
                {"image": "Это поле обязательно"}, 
                code='required'
            )
        return data

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {"ingredients": "Нужно выбрать ингредиент!"},
                code=HTTPStatus.BAD_REQUEST,
            )

        ingredient_ids = [item["id"].id for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться!"},
                code=HTTPStatus.BAD_REQUEST,
            )

        return value

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        instance.ingredients.clear()
        instance = super().update(instance, validated_data)
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeListSerializer(instance, context=context).data


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор для рецептов в подписках."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time", "image")


class FollowSerializer(serializers.ModelSerializer):
    """Serializer подписок с информацией об авторе и его рецептах."""

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj) -> bool:
        return True

    def _get_author_recipes(self, author) -> QuerySet:
        """Возвращает QuerySet рецептов автора с учётом лимита."""
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = author.recipes.all()
        return (
            queryset[: int(limit)] if limit and limit.isdigit() else queryset
        )

    def get_recipes(self, obj) -> list:
        """Список рецептов автора."""
        recipes = self._get_author_recipes(obj.author)
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj) -> int:
        """Количество рецептов автора (оптимизация через кэш QuerySet)."""
        return obj.author.recipes.count()

    def validate(self, data):
        """Проверка возможности подписки."""
        author = self.context["author"]
        user = self.context["request"].user

        if user == author:
            raise ValidationError(
                "Нельзя подписаться на себя!", code=HTTPStatus.BAD_REQUEST)
        if user.follower.filter(author=author).exists():
            raise ValidationError(
                "Вы уже подписаны!", code=HTTPStatus.BAD_REQUEST)
        return data
