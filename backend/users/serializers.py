from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer для чтения / создания пользователя модели User.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
            "avatar",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "is_subscribed": {"read_only": True},
            "avatar": {"read_only": True},
        }

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return request.user.follower.filter(author=obj).exists()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
