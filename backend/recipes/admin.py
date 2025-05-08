from django.contrib import admin
from django.contrib.admin import display
from django.utils.translation import gettext_lazy as _

from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)
from identity.models import Follow


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'get_favorites_count',
        'get_ingredients', 'cooking_time'
    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username', 'tags__name')
    readonly_fields = ('get_favorites_count',)
    inlines = (RecipeIngredientInline,)

    @display(description='Количество в избранном')
    def get_favorites_count(self, obj):
        return obj.favorite_set.count()

    @display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join([
            f'{ingredient.name} ({ingredient.measurement_unit})'
            for ingredient in obj.ingredients.all()
        ])


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Follow, FollowAdmin)