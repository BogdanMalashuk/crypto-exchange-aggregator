from rest_framework import generics, permissions, viewsets
from .serializers import RegisterSerializer, ApiKeySerializer, UserSerializer
from .models import ApiKey, User
from .permissions import ApiKeyAccessPermission, UserManagementPermission


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ApiKeyListCreateView(generics.ListCreateAPIView):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, ApiKeyAccessPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "admin":
            return ApiKey.objects.select_related("user").all()
        return ApiKey.objects.filter(user=user)


class ApiKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, ApiKeyAccessPermission]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "admin":
            return ApiKey.objects.select_related("user").all()
        return ApiKey.objects.filter(user=user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, UserManagementPermission]
