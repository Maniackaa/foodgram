from rest_framework import permissions


class ForUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == "POST" and request.user.is_anonymous:
            return True
        if (
            request.user.is_authenticated
            and request.method in permissions.SAFE_METHODS
        ):
            return True


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.role == "admin"
