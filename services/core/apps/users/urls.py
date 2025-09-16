from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ApiKeyListCreateView, ApiKeyDetailView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("keys/", ApiKeyListCreateView.as_view(), name="apikey-list-create"),
    path("keys/<int:pk>/", ApiKeyDetailView.as_view(), name="apikey-detail"),
]

urlpatterns += router.urls
