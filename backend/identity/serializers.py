from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer

from recipes.models import Follow
from identity.models import User

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''Сериализатор для пользователя'''
    avatar = Base64ImageField(required=False, max_length=None)
    is_subscribed = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'avatar',
            'bio'
        )
        read_only_fields = ('is_subscribed', 'recipes_count')

    def get_is_subscribed(self, obj):
        '''Проверка подписки пользователя'''
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Создание пользователя'''
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует'
            )
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким именем уже существует'
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me"'
            )
        return value


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:  # 2MB
                raise serializers.ValidationError(
                    'Размер файла не может превышать 2MB'
                )
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError(
                    'Файл должен быть изображением'
                )
        return value
