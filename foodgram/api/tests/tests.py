from http import HTTPStatus

from app.models import Ingredient, IngredientInRecipe, Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    recipe = Recipe()
    tag = Tag()
    ingredient = Ingredient()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.tag = Tag.objects.create(
            name="Завтрак", color="#E26C2D", slug="breakfast"
        )
        cls.ingredient = Ingredient.objects.create(
            name="Картошка", measurement_unit="г"
        )
        cls.recipe = Recipe.objects.create(
            name="Тестовый рецепт",
            author=cls.user,
            image="data:image/png;base64,iVBORg==",
            text="Описание",
            cooking_time=10,
        )
        cls.ingredient_in_recipe = IngredientInRecipe.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient, amount=100
        )
        cls.recipe.tags.add(cls.tag)

    def setUp(self):
        self.guest_client = Client()
        self.user_client = Client()
        self.user_client.force_login(user=self.user)

    def test_urls_get_for_guest(self):
        """Проверка доступа неавторизованного пользователя"""
        url_names_guest = {
            "/api/": HTTPStatus.OK,
            "/api/users/": HTTPStatus.OK,
            "/api/users/1/": HTTPStatus.UNAUTHORIZED,
            "/api/users/me/": HTTPStatus.UNAUTHORIZED,
            "/api/tags/": HTTPStatus.OK,
            "/api/tags/1/": HTTPStatus.OK,
            "/api/recipes/": HTTPStatus.OK,
            "/api/recipes/1/": HTTPStatus.OK,
            "/api/recipes/download_shopping_cart/": HTTPStatus.UNAUTHORIZED,
            "/api/users/subscriptions/": HTTPStatus.UNAUTHORIZED,
            "/api/ingredients/": HTTPStatus.OK,
            "/api/ingredients/1/": HTTPStatus.OK,
        }
        for url, status in url_names_guest.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                print(response.data)
                self.assertEqual(response.status_code, status)

    def test_urls_get_for_authorized(self):
        """Проверка доступа авторизованного пользователя"""
        url_names_user = {
            "/api/": HTTPStatus.OK,
            "/api/users/": HTTPStatus.OK,
            "/api/users/1/": HTTPStatus.OK,
            "/api/users/me/": HTTPStatus.OK,
            "/api/tags/": HTTPStatus.OK,
            "/api/tags/1/": HTTPStatus.OK,
            "/api/recipes/": HTTPStatus.OK,
            "/api/recipes/1/": HTTPStatus.OK,
            "/api/recipes/download_shopping_cart/": HTTPStatus.NO_CONTENT,
            "/api/users/subscriptions/": HTTPStatus.OK,
            "/api/ingredients/": HTTPStatus.OK,
            "/api/ingredients/1/": HTTPStatus.OK,
        }
        for url, status in url_names_user.items():
            with self.subTest(url=url):
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, status)
