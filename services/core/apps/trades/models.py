from django.db import models
from apps.users.models import Profile


class Trade(models.Model):
    class Side(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="trades")
    exchange = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=10, choices=Side.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    profit = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField()
    lot = models.ForeignKey(
        "Lot",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trades"
    )

    def __str__(self):
        return f"{self.exchange} {self.symbol} {self.side} {self.amount} @ {self.price}"


class Lot(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="lots")
    exchange = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    buy_price = models.DecimalField(max_digits=20, decimal_places=8)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} {self.amount}/{self.amount} @ {self.buy_price}"


class ProcessedEvent(models.Model):
    event_id = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id
