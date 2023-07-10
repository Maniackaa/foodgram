from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(unique=True, max_length=200,
                            verbose_name='Название')
    color = models.CharField(unique=True, max_length=7,
                             verbose_name='Цвет в HEX')
    slug = models.SlugField(unique=True,
                            verbose_name='Уникальный слаг')

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Ед. изм.')

    class Meta:
        unique_together = ['name', 'measurement_unit']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(unique=True, max_length=200)
    tags = models.ManyToManyField(to=Tag, related_name='receipt_tags',
                                  verbose_name='Список тегов')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientInRecipe',
                                         verbose_name='Список ингредиентов')
    image = models.ImageField(upload_to='images/',
                              verbose_name='Ссылка на картинку на сайте')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)')

    class Meta:
        unique_together = ['name', 'author']
        ordering = ['-pk']

    def __str__(self):
        return f'{self.id}. {self.name}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='components')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return (
            f'{self.id}. '
            f'{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class ShopCart(models.Model):
    author = models.ForeignKey(User, related_name='cart',
                               on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='cart',
                               on_delete=models.CASCADE)


class Favorite(models.Model):
    author = models.ForeignKey(User, related_name='author_favorites',
                               on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='author_favreceipts',
                               on_delete=models.CASCADE)

    class Meta:
        unique_together = ['author', 'recipe']


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='followed',
                               on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'author']


class Session(models.Model):
    name = models.CharField
    session = models.FileField(upload_to='sessions')
