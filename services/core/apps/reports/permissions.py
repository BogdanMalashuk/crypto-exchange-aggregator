from rest_framework.permissions import BasePermission


class ReportAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ("admin", "analyst"):
            return True
        return obj.user == request.user
