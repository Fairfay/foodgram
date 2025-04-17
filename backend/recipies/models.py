from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import CustomUser


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название тега', max_length=200, unique=True)
    color = ColorField('Код цвета', default='#000000', max_length=7)
    slug = models.SlugField('Слаг тега', max_length=200, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipes',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Ссылка на изображение',
                              upload_to='recipes/images/')
    text = models.TextField('Описание рецепта')
    pub_date = models.DateTimeField(auto_now_add=True)
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в мин',
        validators=[
            MinValueValidator(1, 'Время приготовления не может '
                                 'быть меньше 1 минуты')
        ],
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт {self.name} | Составил: {self.author}'


class IngredientRecipes(models.Model):
    id = models.AutoField(primary_key=True)
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[RegexValidator(r'^[0-9]+$',
                                   'Значение должно быть целым числом'
                                   )],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipes', 'ingredients'],
                name='unique_ingredients_recipes'
            )
        ]

    def __str__(self):
        return f'{self.recipes.name}:{self.ingredients.name}'


class ShoppingList(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(Recipe,
                                verbose_name='Рецепт',
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'], name='unique_recipes_list'
            )
        ]

    def __str__(self):
        return f'Список покупок пользователя {self.user.username}'


class RecipeFavorites(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser, verbose_name='Пользователь', on_delete=models.CASCADE
    )
    recipes = models.ForeignKey(Recipe,
                                verbose_name='Рецепт',
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'], name='unique_recipes_favorites'
            )
        ]

    def __str__(self):
        return f'Список избранных рецептов {self.user.username}'


class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
            models.CheckConstraint(
                name='user_is_not_author',
                check=~models.Q(user=models.F('author'))
            ),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
