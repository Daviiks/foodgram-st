﻿from django.contrib import admin
from django.db.models import Count
from .models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
)


class IngredientsInline(admin.TabularInline):
    """
    Админка для интеграции добавления ингридиентов в рецепты.
    """

    model = Recipe.ingredients.through
    extra = 3


class SubscrationAdmin(admin.ModelAdmin):
    """
    Админка подписок.
    """

    list_display = ("user", "author")
    list_filter = ("author",)
    search_fields = ("user",)


class FavoriteAdmin(admin.ModelAdmin):
    """
    Админка избранных рецептов.
    """

    list_display = ("author", "recipe")
    list_filter = ("author",)
    search_fields = ("author",)


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админка покупок.
    """

    list_display = ("author", "recipe")
    list_filter = ("author",)
    search_fields = ("author",)


class IngredientRecipeAdmin(admin.ModelAdmin):
    """
    Админка ингридентов для рецептов.
    """

    list_display = (
        "id",
        "recipe",
        "ingredient",
        "amount",
    )
    list_filter = ("recipe", "ingredient")
    search_fields = ("name",)


class RecipeAdmin(admin.ModelAdmin):
    """
    Админка рецептов.
    """

    list_display = ("id", "author", "name", "pub_date", "in_favorite")
    search_fields = ("name", "author__username")
    list_filter = ("pub_date", "author")
    empty_value_display = "-пусто-"
    inlines = [IngredientsInline]
    list_select_related = ("author",)

    """
    Просмотр кол-ва добавленных рецептов в избранное
    """
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(favorites_count=Count("favorite"))
        )

    def in_favorite(self, obj):
        return obj.favorites_count

    in_favorite.short_description = "В избранном (раз)"
    in_favorite.admin_order_field = "favorites_count"


class IngredientAdmin(admin.ModelAdmin):
    """
    Админка ингридиентов.
    """

    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    search_fields = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Follow, SubscrationAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
