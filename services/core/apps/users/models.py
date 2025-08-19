from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        ANALYST = "analyst", "Analyst"
        TRADER = "trader", "Trader"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TRADER)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ({self.role})"


class ApiKey(models.Model):
    class Exchange(models.TextChoices):
        BINANCE = "binance", "Binance"
        BYBIT = "bybit", "Bybit"

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="api_keys")
    exchange = models.CharField(max_length=20, choices=Exchange.choices)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["profile", "exchange"], name="unique_profile_exchange")
        ]

    def __str__(self):
        return f"{self.profile.user.email} - {self.exchange}"
