from django.contrib import admin

from .models import (
    Recipe, Tag, Ingredient, IngredientInRecipe, ShopCart,
    Favorite, Follow,
)


class IngrInline(admin.StackedInline):
    model = IngredientInRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorite_count')
    list_display_links = ['pk', 'name', 'author']
    list_filter = ('author', 'name', 'tags')
    inlines = [IngrInline]

    def favorite_count(self, obj):
        return obj.author_favreceipts.all().count()

    favorite_count.short_description = 'Добавлено в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_display_links = ('pk', 'name')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShopCart)
admin.site.register(Favorite)
admin.site.register(Follow)
