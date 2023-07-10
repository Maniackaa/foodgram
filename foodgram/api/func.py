from rest_framework import status

from app.models import IngredientInRecipe
from django.db.models import Sum
from django.http import HttpResponse


def get_shopping_cart_text(self, request, author):
    total_in_recipes = (
        IngredientInRecipe.objects.filter(recipe__cart__author=author)
        .values(
            "ingredient__name",
            "ingredient__measurement_unit",
            "ingredient__recipe__name",
        )
        .annotate(amounts=Sum("amount", distinct=True))
        .order_by("ingredient__name")
    )
    recipes_names = [
        name for name in total_in_recipes.values("ingredient__recipe__name")
    ]
    names = set(
        [
            recipes_name["ingredient__recipe__name"]
            for recipes_name in recipes_names
        ]
    )
    text = f'Ингридиенты для рецептов {", ".join(names)}:\n\n'
    for num, component in enumerate(total_in_recipes, 1):
        text += (
            f'{num}) {component["ingredient__name"]}: '
            f'{component["amounts"]} '
            f'{component["ingredient__measurement_unit"]}\n'
        )
    response = HttpResponse(
        text, content_type="text/plain", status=status.HTTP_200_OK
    )
    return response
