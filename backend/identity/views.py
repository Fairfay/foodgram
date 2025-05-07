from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from api.serializers import FollowSerializer
from identity.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    AvatarSerializer
)
from recipes.models import Follow
from .models import User


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    def get_permissions(self):
        public_actions = [
            'list', 'retrieve', 'create',
            'activation', 'reset_password',
            'reset_password_confirm', 'token_create'
        ]
        if self.action in public_actions:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'patch'],
        permission_classes=[IsAuthenticated],
        serializer_class=AvatarSerializer
    )
    def avatar(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = request.user.follower.all()
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)

        if request.method == 'POST':
            if author == request.user:
                return Response(
                    {'error': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Follow.objects.filter(
                user=request.user,
                author=author
            ).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follow.objects.create(user=request.user, author=author)
            serializer = FollowSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = get_object_or_404(
            Follow,
            user=request.user,
            author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['put', 'patch'],
        permission_classes=[IsAuthenticated],
        serializer_class=AvatarSerializer
    )
    def avatar(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)