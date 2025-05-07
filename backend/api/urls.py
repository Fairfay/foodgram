from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    FollowViewSet, IngredientViewSet,
    RecipeViewSet, TagViewSet
)
from identity.views import CustomUserViewSet

app_name = "api"

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', FollowViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path("", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken"))
]