from rest_framework import generics, permissions
from .serializers import RegisterSerializer, ProfileSerializer, ApiKeySerializer
from .models import ApiKey
from .permissions import ApiKeyAccessPermission
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ApiKeyListCreateView(generics.ListCreateAPIView):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, ApiKeyAccessPermission]

    def get_queryset(self):
        user = self.request.user
        try:
            role = user.profile.role
        except ObjectDoesNotExist:
            raise PermissionDenied("User has not profile")

        if role == "admin":
            return ApiKey.objects.select_related("profile", "profile__user").all()
        return ApiKey.objects.filter(profile=user.profile)


class ApiKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated, ApiKeyAccessPermission]

    def get_queryset(self):
        user = self.request.user
        try:
            role = user.profile.role
        except ObjectDoesNotExist:
            raise PermissionDenied("User has not profile")

        if role == "admin":
            return ApiKey.objects.select_related("profile", "profile__user").all()
        return ApiKey.objects.filter(profile=user.profile)
