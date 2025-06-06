from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.serializers import SetPasswordSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from api.paginations import ApiPagination
from api.permissions import IsCurrentUserOrAdminOrReadOnly
from api.serializers import FollowSerializer
from .models import User
from .serializers import UserCreateSerializer, UserSerializer, UserAvatarSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для пользователя / подписок."""

    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly,)
    pagination_class = ApiPagination
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'avatar':
            return UserAvatarSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Получение профиля текущего пользователя."""
        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        if request.method == 'PUT':
            return self._update_avatar(request)
        return self._delete_avatar(request)

    def _update_avatar(self, request):
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def _delete_avatar(self, request):
        if not request.user.avatar:
            return Response(
                {'error': 'Аватара не существует'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        """Изменение пароля пользователя."""
        serializer = SetPasswordSerializer(
            data=request.data, 
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data["new_password"])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        """Создание и удаление подписки."""
        author = get_object_or_404(User, id=kwargs.get("pk"))
        user = request.user

        if request.method == "POST":
            if user.follower.filter(author=author).exists():
                return Response(
                    {"errors": "Вы уже подписаны на этого автора"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FollowSerializer(
                data=request.data,
                context={"request": request, "author": author},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = user.follower.filter(author=author).first()
        if not subscription:
            return Response(
                {"errors": "Вы не подписаны на этого автора"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, 
        methods=["get"], 
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Отображение всех подписок пользователя."""
        follows = request.user.follower.all()
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            pages, 
            many=True, 
            context={"request": request}
        )
        return self.get_paginated_response(serializer.data)