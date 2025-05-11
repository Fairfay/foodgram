from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 150
AVATAR_UPLOAD_PATH = 'users/avatars/'


class User(AbstractUser):
    """Переопределенная модель пользователя"""
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_LENGTH,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to=AVATAR_UPLOAD_PATH,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель для подписок пользователей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
