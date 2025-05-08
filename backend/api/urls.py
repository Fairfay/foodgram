from django.urls import include, path
from rest_framework.routers import DefaultRouter
from identity.views import CustomUserViewSet
from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('recipes/<int:recipe_id>/favorite/', 
         RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}), 
         name='recipe-favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/', 
         RecipeViewSet.as_view({'post': 'shopping_cart', 'delete': 'shopping_cart'}), 
         name='recipe-shopping-cart'),
    path('recipes/download_shopping_cart/', 
         RecipeViewSet.as_view({'get': 'download_shopping_cart'}), 
         name='download-shopping-cart'),
]