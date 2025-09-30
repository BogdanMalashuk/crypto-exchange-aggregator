from rest_framework import generics, permissions, viewsets, status
from .serializers import (RegisterSerializer,
                          ApiKeySerializer,
                          UserSerializer,
                          PasswordResetRequestSerializer,
                          PasswordResetConfirmSerializer)
from .models import ApiKey, User
from .permissions import ApiKeyAccessPermission, UserManagementPermission
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.response import Response
from .tokens import password_reset_token
from .tasks import send_password_reset_email


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


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If this email exists, password reset sent."}, status=200)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)

        message = (
            "Вы запросили восстановление пароля.\n\n"
            f"UID: {uid}\n"
            f"TOKEN: {token}\n\n"
        )

        send_password_reset_email.delay(
            subject="Password Reset",
            recipient=email,
            body=message,
        )

        return Response({"detail": "Password reset e-mail has been sent."}, status=200)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Invalid token."}, status=400)

        if not password_reset_token.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset."}, status=200)
