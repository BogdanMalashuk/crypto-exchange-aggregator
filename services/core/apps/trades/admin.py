from django.contrib import admin
from .models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "exchange", "symbol", "side", "amount", "price", "timestamp")
    list_filter = ("exchange", "side")
