from rest_framework import serializers

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Follow
from identity.models import User


class CustomUserSerializer(UserSerializer):
    '''Кастотмный сериализатор пользователя'''

    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('__all__')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return Follow.objects.filter(follower=user, following=obj).exists()
