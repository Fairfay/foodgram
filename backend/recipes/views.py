from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientRecipe,
    RecipeFavorite, ShoppingList, Follow
)
from identity.models import CustomUser
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeFavoriteSerializer, ShoppingListSerializer, FollowSerializer
)
from api.filters import IngredientSearchFilter, RecipesFilter
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [IngredientSearchFilter]
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.annotate(favorites_count=Count('favorited_by'))
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filterset_class = RecipesFilter
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return (super().get_queryset()
                .select_related('author')
                .prefetch_related('tags', 'ingredient_amounts__ingredient'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            RecipeFavorite.objects.get_or_create(user=request.user, recipe=recipe)
            serializer = RecipeFavoriteSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        RecipeFavorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
            serializer = ShoppingListSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        ShoppingList.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        items = (IngredientRecipe.objects
                 .filter(recipe__in_shopping_lists__user=request.user)
                 .values('ingredient__name', 'ingredient__measurement_unit')
                 .annotate(total_amount=Sum('amount')))
        lines = [f"{i['ingredient__name']} - {i['total_amount']} {i['ingredient__measurement_unit']}" for i in items]
        content = "\n".join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(CustomUser, id=self.kwargs['id'])
        follow, created = Follow.objects.get_or_create(follower=request.user, following=author)
        serializer = self.get_serializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author = get_object_or_404(CustomUser, id=self.kwargs['id'])
        Follow.objects.filter(follower=request.user, following=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
