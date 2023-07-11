from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientSearch
from api.func import get_shopping_cart_text
from api.paginators import ApiPagination
from api.permission import ForUsers, IsOwnerOrAdmin
from api.serializers import (
    ChangePassSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerilizer,
    RecipeWriteSerializer,
    ShopCartSerializer,
    TagSerializer,
    UserRegSerializer,
)
from app.models import Favorite, Follow, Ingredient, Recipe, ShopCart, Tag

User = get_user_model()


class UsersViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny, ForUsers)
    pagination_class = ApiPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(
            IsAuthenticated,
            IsOwnerOrAdmin,
        ),
        url_path="me",
    )
    def current_user_profile(self, request):
        serializer = UserRegSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated, IsOwnerOrAdmin),
        url_path="set_password",
    )
    def change_password(self, request):
        serializer = ChangePassSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"Result": "Пароль успешно изменен"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        follows = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get("pk"))
        user = self.request.user
        if request.method == "POST":
            serializer = FollowSerializer(
                data=request.data,
                context={"request": request, "author": author},
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(
                    {"Подписка!": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"errors": "Не найдено"}, status=status.HTTP_404_NOT_FOUND
            )
        if Follow.objects.filter(author=author, user=user).exists():
            Follow.objects.get(author=author).delete()
            return Response("Отписка!", status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Не найдено"}, status=status.HTTP_404_NOT_FOUND
        )


class RegView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TagsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = [IngredientSearch]
    search_fields = ["name"]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerilizer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerilizer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("pk"))
        user = self.request.user
        if request.method == "POST":
            if Favorite.objects.filter(author=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в избранном!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        # Если DELETE
        if not Favorite.objects.filter(author=user, recipe=recipe).exists():
            return Response(
                {"errors": "Объект не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )
        Favorite.objects.get(author=user, recipe=recipe).delete()
        return Response(
            "Рецепт удалён из избранного.", status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("pk"))
        user = self.request.user
        if request.method == "POST":
            if ShopCart.objects.filter(author=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже в корзине!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = ShopCartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        # Если DELETE
        if not ShopCart.objects.filter(author=user, recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )
        ShopCart.objects.get(recipe=recipe).delete()
        return Response(
            "Рецепт удалён из корзины.", status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        author = User.objects.get(id=self.request.user.pk)
        if author.cart.exists():
            text = get_shopping_cart_text(self, request, author)
            response = HttpResponse(
                text, content_type="text/plain", status=status.HTTP_200_OK)
            return response
        return Response("Ничего нет", status=status.HTTP_204_NO_CONTENT)
