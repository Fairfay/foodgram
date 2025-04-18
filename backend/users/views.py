from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

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

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = self.request.user.follower.all()
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
