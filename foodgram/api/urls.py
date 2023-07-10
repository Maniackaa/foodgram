from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagsViewSet,
    UsersViewSet, SessionViewSet,
)

app_name = "api"

v1_router = DefaultRouter()
v1_router.register("users", UsersViewSet, basename="users")
v1_router.register("recipes", RecipeViewSet, basename="recipes")
v1_router.register("ingredients", IngredientViewSet, basename="ingredients")
v1_router.register("tags", TagsViewSet, basename="tags")
v1_router.register('sessions', SessionViewSet, basename='sessions')


urlpatterns = [
    path("", include(v1_router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("api-token-auth/", views.obtain_auth_token),
    # path("sessions", SessionViewSet.as_view())
]
