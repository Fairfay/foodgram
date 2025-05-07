from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя"""
    avatar = models.ImageField(
        'Аватар',
        blank=True,
        upload_to='avatars/',
        help_text='Загрузите изображение в формате JPG или PNG'
    )

    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username

    def get_subscribers_count(self):
        return self.following.count()

    def get_recipes_count(self):
        return self.recipes.count()
