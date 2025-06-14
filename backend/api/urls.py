﻿from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, ShortLinkRedirectView
from users.views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename="users")
router.register('recipes', RecipeViewSet, basename="recipes")
router.register('ingredients', IngredientViewSet, basename="ingredients")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', 
         UserViewSet.as_view({'put': 'avatar', 'delete': 'avatar'}), 
         name='user-avatar'
         ),
    path('s/<str:short_code>/', 
         ShortLinkRedirectView.as_view(), 
         name='short-link-redirect'),
]
