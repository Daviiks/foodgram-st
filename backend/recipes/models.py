from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, F
from users.models import User
import secrets

MIN_AMOUNT = 1
MAX_AMOUNT = 32000
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000

class Ingredient(models.Model):
    """Ингридиенты для рецептов."""

    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=200,
        db_index=True,
        help_text="Введите название ингредиента",
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200,
        help_text="Введите единицу измерения",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    """
    Рецепты.
    У автора не может быть создано более одного рецепта с одним именем.
    """

    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200,
        help_text="Введите название рецепта",
        db_index=True,
    )

    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe", verbose_name="Ингредиенты"
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME, "Минимальное время приготовления"
                ),
            MaxValueValidator(
                MAX_COOKING_TIME, "Максимальное время приготовления"
                )
        ],
        help_text="Укажите время приготовления рецепта в минутах",
    )
    
    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Опишите приготовление рецепта",
        max_length=256
    )

    image = models.ImageField(
        verbose_name="Картинка рецепта",
        upload_to="recipes/images/",
        help_text="Добавьте изображение рецепта",
        default=None,
    )

    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        help_text="Автор рецепта",
        related_name="recipes",
    )

    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]
        default_related_name = "recipe"
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "author"], name="unique_recipe"
            )
        ]

    def __str__(self):
        return f"{self.name}"


class IngredientRecipe(models.Model):
    """
    Ингридиенты для рецепта.
    """

    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe_ingredients",
        verbose_name="Название рецепта",
        on_delete=models.CASCADE,
        help_text="Выберите рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
        help_text="Укажите ингредиенты",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_AMOUNT, "Минимальное количество ингредиентов 1"
                ),
            MaxValueValidator(
                MAX_AMOUNT, "Максимальное количество ингредиентов 32000"
                )
        ],
        verbose_name="Количество",
        help_text="Укажите количество ингредиента",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Cостав рецепта"
        verbose_name_plural = "Состав рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_ingredients"
            )
        ]

    def __str__(self):
        return f"{self.ingredient} {self.amount}"


class ShoppingCart(models.Model):
    """
    Корзина покупок.
    """

    author = models.ForeignKey(
        User,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shopping_cart",
        verbose_name="Рецепт для приготовления",
        on_delete=models.CASCADE,
        help_text="Выберите рецепт для приготовления",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "recipe"], name="unique_cart"
            )
        ]

    def __str__(self):
        return f"{self.recipe}"


class Favorite(models.Model):
    """
    Избранные рецепты пользователя.
    """

    author = models.ForeignKey(
        User,
        related_name="favorite",
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorite",
        on_delete=models.CASCADE,
        verbose_name="Рецепты",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Избранные рецепты"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "recipe"], name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"{self.recipe}"


class Follow(models.Model):
    """
    Подписки на авторов созданных рецептов.
    """

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="follower",
        on_delete=models.CASCADE,
        help_text="Текущий пользователь",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Подписка",
        related_name="followed",
        on_delete=models.CASCADE,
        help_text="Подписаться на автора рецепта(ов)",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Мои подписки"
        verbose_name_plural = "Мои подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_following"
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")),
                name="no_self_following",
                violation_error_message="Нельзя подписаться на самого себя",
            ),
        ]

    def __str__(self):
        return f"Вы подписаны на {self.author}"

def generate_short_code():
    return secrets.token_urlsafe(8)[:8]

class ShortLink(models.Model):
    short_code = models.CharField(
        max_length=20, 
        primary_key=True, 
        default=generate_short_code
    )
    destination = models.TextField()  # URL назначения
    recipe = models.OneToOneField(
        'Recipe', 
        on_delete=models.CASCADE,
        related_name='short_link'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Short Link'
        verbose_name_plural = 'Short Links'