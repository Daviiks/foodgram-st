﻿from django.db import models
from django.core.validators import  RegexValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Класс пользователя.
    """

    USER = "user"
    ADMIN = "admin"
    ROLE_USER = [(USER, "Пользователь"), (ADMIN, "Администратор")]
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message='Имя пользователя может содержать только буквы, \
        цифры и @/./+/-/_'
    )
    email = models.EmailField("email-адрес", unique=True)
    username = models.CharField("Логин", max_length=150, unique=True,
                                validators=[username_validator])
    role = models.CharField(
        max_length=150,
        choices=ROLE_USER,
        default=USER,
        verbose_name="Пользовательская роль",
    )
    avatar = models.ImageField(upload_to='users/avatars/',
        blank=True, null=True,
        verbose_name='Аватар',
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.username
