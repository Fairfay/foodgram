from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from identity.models import User
from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    """Фильтр для поиска ингредиентов по началу названия"""
    search_param = 'name'


class RecipesFilter(FilterSet):
    """Фильтрация рецептов по автору, тегам, избранному и списку покупок"""
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='author'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(in_shopping_lists__user=user)
        return queryset.exclude(in_shopping_lists__user=user)
