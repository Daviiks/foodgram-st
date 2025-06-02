from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from djoser.serializers import SetPasswordSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from api.paginations import ApiPagination
from api.permissions import IsCurrentUserOrAdminOrReadOnly
from api.serializers import FollowSerializer
from .models import User
from .serializers import UserSerializer, UserAvatarSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для пользователя / подписок."""

    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly,)
    pagination_class = ApiPagination
    serializer_class = UserSerializer

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Кастомное получение профиля пользователя."""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=['PUT'], url_path='me/avatar',
           permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        """
        Кастомное изменение пароля с помощью Serializer
        из пакета djoser.
        """
        serializer = SetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data["new_password"])
        request.user.save()
        return Response(
            "Пароль успешно изменен", 
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        """Создание и удаление подписки."""
        author = get_object_or_404(User, id=self.kwargs.get("pk"))
        user = self.request.user
        if request.method == "POST":
            serializer = FollowSerializer(
                data=request.data,
                context={"request": request, "author": author},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, user=user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        subscription = get_object_or_404(
            user.follower,
            author=author
        )
        subscription.delete()
        return Response(
            "Успешная отписка", 
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        follows = request.user.follower.all()
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
