from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    """
    Модель тегов, цвет хранится в HEX-формате.
    """
    name = models.CharField('Название тега', max_length=200, unique=True)
    color = models.CharField('Цвет тега', max_length=7, unique=True)
    slug = models.SlugField(
        'Слаг тега',
        max_length=200,
        unique=True,
        validators=(RegexValidator(regex=r'^[-a-zA-Z0-9_]+$',),)
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингридиентов и их единиц измерения.
    """
    name = models.CharField(
        'Название ингридиента',
        max_length=200,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Единицы измерения ингридиента',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredients'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.
    """
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField('Название рецепта', max_length=200,)
    image = models.ImageField('Картинка рецепта', upload_to='recipes/')
    text = models.TextField('Описание рецепта',)
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
        verbose_name='Ингридиенты рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления рецепта (в минутах)',
        validators=(
            MinValueValidator(
                limit_value=1,
                message='Время приготовления не может быть менее 1 минуты'
            ),
        ),
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """
    Модель, связывающая рецепты с ингредиентами
    и содержащая колличество ингредиентов.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=(
            MinValueValidator(
                limit_value=1,
                message='Количество ингредиентов не может быть менее 1',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredients_recipe'
            ),
        )

    def __str__(self):
        return f'Содержание {self.ingredient} в рецепте {self.recipe}.'


class ShoppingCart(models.Model):
    """
    Модель, содержащая данные о пользователях и
    добавленных ими в список покупок рецептах.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке покупок {self.user}.'


class Favorite(models.Model):
    """
    Модель, содержащая данные о пользователях и
    добавленных ими в избранное рецептах.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorites'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке избранного {self.user}.'
