from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet
from users.views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename="users")
router.register('recipes', RecipeViewSet, basename="recipes")
router.register('ingredients', IngredientViewSet, basename="ingredients")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('/users/me/avatar/', UserViewSet.as_view({'put': 'avatar'}), 
         name='user-avatar'
         ),
]
