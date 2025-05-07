from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from recipes.models import (
    Follow, Ingredient, Recipe, RecipeIngredient,
    Favorite, ShoppingCart, Tag
)
from identity.models import User
from api.filters import IngredientSearchFilter, RecipesFilter
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    FollowSerializer, IngredientSerializer,
    RecipeSerializer, TagSerializer, UserSerializer
)


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Теги'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Ингредиенты'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [IngredientSearchFilter]
    search_fields = ['^name']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Рецепты'''

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipesFilter
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        favorite = get_object_or_404(Favorite, user=request.user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        cart_item = get_object_or_404(ShoppingCart, user=request.user, recipe=recipe)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )

        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class FollowViewSet(viewsets.ModelViewSet):
    '''Подписки'''

    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        
        if author == request.user:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow = Follow.objects.create(user=request.user, author=author)
        serializer = self.get_serializer(follow.author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        follow = get_object_or_404(
            Follow,
            user=request.user,
            author_id=author_id
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)