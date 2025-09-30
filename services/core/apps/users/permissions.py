from rest_framework.permissions import BasePermission


class ApiKeyAccessPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == "analyst":
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == user.Role.ADMIN:
            return True
        return obj.user == user


class UserManagementPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return user.role == user.Role.ADMIN
        return True
