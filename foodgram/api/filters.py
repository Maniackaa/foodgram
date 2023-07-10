import django_filters

from django_filters.rest_framework import FilterSet
from rest_framework.filters import SearchFilter

from app.models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = django_filters.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = django_filters.NumberFilter(
        method="filter_is_in_shop_cart"
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ["is_favorited", "author", "is_in_shopping_cart", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(
                author_favreceipts__author=self.request.user
            )
        return queryset

    def filter_is_in_shop_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(cart__author=self.request.user)
        return queryset


class IngredientSearch(SearchFilter):
    search_param = "name"
