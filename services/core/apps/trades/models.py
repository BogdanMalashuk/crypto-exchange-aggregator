from django.db import models
from users.models import Profile


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

    def __str__(self):
        return f"{self.exchange} {self.symbol} {self.side} {self.amount} @ {self.price}"
