from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer

from recipies.models import Follow
from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    '''Сериализатор для пользователя'''
    avatar = Base64ImageField(required=False, max_length=None)
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        '''Проверка подписки пользователя'''
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Создание пользователя'''
    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ('email',
                  'id',
                  'password',
                  'username',
                  'first_name',
                  'last_name',
                  'avatar',)
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'avatar': {'required': False},
        }


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    def update(self, instance, validated_data):
        instance.avatar = validated_data['avatar']
        instance.save()
        return instance
