import rest_framework.pagination
from app.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShopCart,
    Tag,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.validators import EmailValidator
from django.core.validators import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import as_serializer_error
from rest_framework.validators import UniqueValidator

from api.permission import IsOwnerOrAdmin

User = get_user_model()


class UserRegSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        write_only=False,
        validators=[
            EmailValidator(),
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    password = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id", "email")

    def validate(self, attrs: dict):
        print("validate", attrs)
        if attrs.get("password") == "123456":
            raise ValidationError()
        return attrs

    def run_validation(self, *args, **kwargs):
        try:
            print("run_validation", *args, **kwargs)
            return super().run_validation(*args, **kwargs)
        except (
            ValidationError,
            DjangoValidationError,
        ) as exc:
            print("Ошибки валидации (ValidationError, DjangoValidationError)")
            raise ValidationError(detail=as_serializer_error(exc))
        except Exception as exc:
            print("Критическая ошибка при валидации")
            raise ValidationError(detail=as_serializer_error(exc))

    @transaction.atomic
    def create(self, validated_data):
        print("Create")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class ChangePassSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)
    permission_classes = (IsOwnerOrAdmin,)

    def validate(self, attrs: dict):
        user = self.instance
        new_password = attrs.get("new_password")
        if new_password == attrs["current_password"]:
            raise ValidationError("Пароль такой-же")
        if user.check_password(attrs.get("current_password")):
            validate_password(new_password)
            user.set_password(new_password)
            user.save()
            return attrs
        raise ValidationError("Неверный пароль")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        pagination_class = rest_framework.pagination.LimitOffsetPagination


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient.id", read_only=True
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerilizer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        many=True, source="components", read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return ShopCart.objects.filter(recipe=obj).exists()
        return False


class IngredientInRecipeWrite(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )
    ingredients = AddIngredientSerializer(many=True, write_only=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=CurrentUserDefault(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "name",
            "text",
            "cooking_time",
            "author",
            "image",
        )
        read_only_fields = (
            "is_favorited",
            "is_in_shopping_cart",
        )

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        print("in ingredients", ingredients)
        ingredients["ingredients"] = IngredientInRecipeSerializer(
            instance.components.all(), many=True
        ).data
        print("out ingredients:", ingredients)
        return ingredients

    @transaction.atomic
    def create(self, validated_data, *args, **kwargs):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_in_recipe in ingredients:
            ingredient = ingredient_in_recipe["id"]
            amount = ingredient_in_recipe["amount"]
            (
                obj,
                res,
            ) = IngredientInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance: Recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.ingredients.set([])
        instance.tags.set([])
        for ingredient_in_recipe in ingredients:
            ingredient = ingredient_in_recipe["id"]
            amount = ingredient_in_recipe["amount"]
            (
                obj,
                res,
            ) = IngredientInRecipe.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount,
            )
            instance.tags.set(tags)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="recipe.name", read_only=True)
    image = serializers.ImageField(source="recipe.image", read_only=True)
    coocking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(source="recipe", read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "coocking_time")


class ShopCartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="recipe.name", read_only=True)
    image = serializers.ImageField(source="recipe.image", read_only=True)
    coocking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(source="recipe", read_only=True)

    class Meta:
        model = ShopCart
        fields = ("id", "name", "image", "coocking_time")


class RecipeFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "cooking_time",
            "image",
        )


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="author.id", read_only=True)
    email = serializers.EmailField(source="author.email", read_only=True)
    username = serializers.CharField(source="author.username", read_only=True)
    first_name = serializers.CharField(
        source="author.first_name", read_only=True
    )
    last_name = serializers.CharField(
        source="author.last_name", read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, follow):
        user = self.context.get("request").user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=follow.user, author=follow.author
            ).exists()
        return False

    def get_recipes(self, follow):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = Recipe.objects.filter(author=follow.author)
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeFollowSerializer(recipes, many=True).data

    def get_recipes_count(self, follow):
        return Recipe.objects.filter(author=follow.author).count()

    def validate(self, attrs):
        user = self.context["request"].user
        author = self.context["author"]
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                f"Вы уже подписаны на автора {author.username}!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if author == user:
            raise ValidationError(
                "Не положено!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return attrs
