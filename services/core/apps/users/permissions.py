from rest_framework.permissions import BasePermission
from .models import Profile


class ApiKeyAccessPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, "profile"):
            return False
        role = user.profile.role
        if role == Profile.Role.ANALYST:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        role = request.user.profile.role
        if role == Profile.Role.ADMIN:
            return True
        return obj.profile == request.user.profile
