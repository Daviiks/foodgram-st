from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Exists, OuterRef
from recipes.models import (
    Recipe, 
    Ingredient, 
    Favorite, 
    ShoppingCart, 
    User, 
    ShortLink
)
from .serializers import (
    RecipeListSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    RecipeWriteSerializer,
    ShortLinkSerializer,
)
from .services import shopping_cart
from .permissions import IsOwnerOrAdminOrReadOnly
from .filters import IngredientSearchFilter, RecipeFilter
from .paginations import ApiPagination


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Функция для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet Рецептов: [GET, POST, DELETE, PATCH]."""

    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = ApiPagination
    filterset_class = RecipeFilter

    """Проверка нахождения рецепта в избранном у текущего пользователя"""
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        author=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def favorite(self, request, pk=None):
        """Управление списком избранных рецептов."""
        user = request.user

        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"errors": "Рецепта не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )   

        if request.method == "POST":
            if user.favorite.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в избранном!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
            user.favorite.create(recipe=recipe)
            serializer = FavoriteSerializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_item = user.favorite.filter(recipe=recipe).first()
        if not favorite_item:
            return Response(
                {"errors": "Этого рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite_item.delete()
        return Response(
            {"message": "Рецепт успешно удалён из избранного"},
            status=status.HTTP_204_NO_CONTENT, 
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        """Управление списком покупок."""
        recipe_id = kwargs.get("pk")
        user = request.user

        if not Recipe.objects.filter(id=recipe_id).exists():
            return Response(
                {"errors": "Рецепта не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipe = Recipe.objects.get(id=recipe_id)

        if request.method == "POST":
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.shopping_cart.create(recipe=recipe)
            serializer = ShoppingCartSerializer(
                recipe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_item = user.shopping_cart.filter(recipe=recipe).first()
        if not cart_item:
            return Response(
                {"errors": "Этого рецепта в корзине нет"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.delete()
        return Response(
            "Рецепт успешно удалён из списка покупок.",
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        if not request.user.shopping_cart.exists():
            return Response(
                "Список покупок пуст.", status=status.HTTP_404_NOT_FOUND
            )
        return shopping_cart(self, request, request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link, created = ShortLink.objects.get_or_create(
            recipe=recipe,
            destination = f'/recipes/{pk}/'
        )
        serializer = ShortLinkSerializer(short_link, context={'request': request})
        return Response(serializer.data)

class ShortLinkRedirectView(APIView):
    def get(self, request, short_code):
        short_link = get_object_or_404(ShortLink, short_code=short_code)
        return redirect(short_link.destination)