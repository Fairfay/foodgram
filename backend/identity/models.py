from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует.'
        }
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя может содержать только буквы, цифры и @/./+/-/_'
            )
        ],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.'
        }
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-Яa-zA-Z\s-]+$',
                message='Имя может содержать только буквы, пробелы и дефисы'
            )
        ]
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-Яa-zA-Z\s-]+$',
                message='Фамилия может содержать только буквы, пробелы и дефисы'
            )
        ]
    )
    avatar = models.ImageField(
        'Аватар',
        blank=True,
        upload_to='avatars/',
        help_text='Загрузите изображение в формате JPG или PNG'
    )
    bio = models.TextField(
        'О себе',
        max_length=500,
        blank=True
    )
    date_joined = models.DateTimeField(
        'Дата регистрации',
        auto_now_add=True
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.username} ({self.get_full_name()})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    def get_subscribers_count(self):
        return self.following.count()

    def get_recipes_count(self):
        return self.recipes.count()
