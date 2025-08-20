from rest_framework.permissions import BasePermission


class ApiKeyAccessPermission(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated or not hasattr(u, "profile"):
            return False
        role = u.profile.role
        if role == "analyst":
            return False
        return True
