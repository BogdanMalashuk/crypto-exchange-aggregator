from rest_framework.permissions import BasePermission


class ApiKeyAccessPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, "profile"):
            return False
        role = user.profile.role
        if role == "analyst":
            return False
        return True
