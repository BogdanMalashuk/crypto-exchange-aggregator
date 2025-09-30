from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        ANALYST = "analyst", "Analyst"
        USER = "user", "User"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class ApiKey(models.Model):
    class Exchange(models.TextChoices):
        BINANCE = "binance", "Binance"
        BYBIT = "bybit", "Bybit"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    exchange = models.CharField(max_length=20, choices=Exchange.choices)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "exchange"], name="unique_user_exchange")
        ]

    def __str__(self):
        return f"{self.user.email} - {self.exchange}"
