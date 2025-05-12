from django.contrib.auth import get_user_model

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from identity.models import Subscription

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


User = get_user_model()

MIN_AMOUNT = 1
MAX_AMOUNT = 32000
MIN_COOKING_TIME = 1
MAX_RECIPES_IN_SUBSCRIPTION = 3


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'avatar',
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для данных пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя'
            )

        if author.following.filter(user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )

        return data


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в подписках."""
    class Meta:
        model = Recipe
        fields = ('__all__')


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()[:MAX_RECIPES_IN_SUBSCRIPTION]
        return SubscriptionRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создание рецептов"""
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        """Создание ингредиентов рецепта."""
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'].id,
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self._create_recipe_ingredients(instance, ingredients_data)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Recipe must have at least one ingredient'
            )

        ingredients_set = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(
                    'Ingredients must be unique'
                )
            ingredients_set.add(ingredient_id)

        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
