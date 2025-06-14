﻿from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Неавторизованным пользователям разрешён только просмотр.
    Адиминистраторам и авторам рецепта разрешены остальные методы.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_superuser

    
class IsCurrentUserOrAdminOrReadOnly(permissions.BasePermission):
    """
    Неавторизованным пользователям разрешён только просмотр.
    Адиминистраторам и авторизованным пользователям разрешены остальные методы.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user or request.user.is_superuser
