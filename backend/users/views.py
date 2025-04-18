from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from djoser.views import UserViewSet

from api.pagination import CustomPagination
from api.serializers import FollowSerializer
from users.serializers import (CustomUserCreateSerializer,
                               CustomUserSerializer,
                               AvatarSerializer)


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    def get_permissions(self):

        public_actions = [
            'list',
            'retrieve',
            'create',
            'activation',
            'reset_password',
            'reset_password_confirm',
            'token_create',
        ]
        if self.action in public_actions:
            perms = [AllowAny]
        else:
            perms = [IsAuthenticated]
        return [p() for p in perms]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['put', 'patch', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(
            instance=user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        out = CustomUserSerializer(user, context={'request': request})
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = self.request.user.follower.all()
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
