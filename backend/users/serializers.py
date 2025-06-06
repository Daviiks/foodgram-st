from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import RegexValidator
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя с гарантированным форматом ответа
    """
    email = serializers.EmailField(required=True)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Username может содержать только буквы, цифры и @/./+/-/_'
            )
        ]
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, data):
        """Общая валидация всех данных"""
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'Пользователь с таким email уже существует'
            })

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
            'username': 'Пользователь с таким username уже существует'
            })

        return data


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
            "avatar",
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return request.user.follower.filter(author=obj).exists()


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {"avatar": "Это поле обязательно."},
                code='required'
            )
        return attrs
