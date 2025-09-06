from django.db import models
from apps.users.models import Profile


class Trade(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    buy_price = models.DecimalField(max_digits=20, decimal_places=8)
    bought_at = models.DateTimeField()
    sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Trade {self.symbol} by {self.user} - {'Sold' if self.sold else 'Open'}"


class Sale(models.Model):
    trade = models.OneToOneField(Trade, on_delete=models.CASCADE, related_name='sale')
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    sell_price = models.DecimalField(max_digits=20, decimal_places=8)
    profit = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return f"Sale of {self.trade.symbol} for {self.trade.user}"
