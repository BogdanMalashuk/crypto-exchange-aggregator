from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, ApiKeyListCreateView, ApiKeyDetailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),

    path("apikeys/", ApiKeyListCreateView.as_view(), name="apikey-list-create"),
    path("apikeys/<int:pk>/", ApiKeyDetailView.as_view(), name="apikey-detail"),
]
