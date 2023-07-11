from django.db.models import Sum

from app.models import IngredientInRecipe


def get_shopping_cart_text(self, request, author):
    print("get_shopping_cart_text")
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
    names_str = ", ".join(names)
    text = f'Ингридиенты для рецептов {names_str}:\n\n'
    for num, component in enumerate(total_in_recipes, 1):
        text += (
            f'{num}) {component["ingredient__name"]}: '
            f'{component["amounts"]} '
            f'{component["ingredient__measurement_unit"]}\n'
        )
    return text
