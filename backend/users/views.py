from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from djoser.views import UserViewSet

from api.pagination import CustomPagination
from api.serializers import FollowSerializer
from users.serializers import CustomUserCreateSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['put', 'patch'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
        parser_classes=[JSONParser],
    )
    def avatar(self, request):
        user = request.user
        avatar_data = request.data.get('avatar')
        if not avatar_data:
            return Response(
                {'error': 'Поле avatar обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.avatar = avatar_data
        user.save()
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = self.request.user.follower.all()
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
