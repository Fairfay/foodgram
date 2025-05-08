from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Subscription
from .serializers import (
    CustomUserSerializer,
    SubscriptionSerializer,
    UserCreateSerializer
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Custom user viewset."""
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = CustomUserSerializer

    def _change_avatar(self, data):
        """Изменение аватара пользователя."""
        user = self.request.user
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    def get_queryset(self):
        queryset = User.objects.all()
        if self.action == 'subscriptions':
            return queryset.filter(following__user=self.request.user)
        return queryset

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_name='me',
    )
    def me(self, request, *args, **kwargs):
        """Данные о себе"""
        return super().me(request, *args, **kwargs)

    @action(
        methods=['put'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        """Добавление или удаление аватара"""
        serializer = self._change_avatar(request.data)
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        data = request.data
        if 'avatar' not in data:
            data = {'avatar': None}
        self._change_avatar(data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'error': 'You cannot subscribe to yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'error': 'You are already subscribed to this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                subscription.author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data) 