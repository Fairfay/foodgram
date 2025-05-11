from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet
)


router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('users', CustomUserViewSet, basename='users')

recipe_urlpatterns = [
    path(
        '<int:recipe_id>/favorite/',
        RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}),
        name='recipe-favorite'
    ),
    path(
        '<int:recipe_id>/shopping-cart/',
        RecipeViewSet.as_view({
            'post': 'shopping_cart',
            'delete': 'shopping_cart'
        }),
        name='recipe-shopping-cart'
    ),
    path(
        'download-shopping-cart/',
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name='download-shopping-cart'
    ),
]

api_v1_urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/', include(recipe_urlpatterns)),
]

urlpatterns = [
    path('', include(api_v1_urlpatterns)),
]
