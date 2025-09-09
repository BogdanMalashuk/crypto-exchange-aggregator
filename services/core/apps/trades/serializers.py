from rest_framework import serializers
from .models import Trade


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'user', 'symbol', 'quantity', 'buy_price', 'bought_at', 'sold', 'sold_at']
        read_only_fields = ['id', 'sold', 'sold_at']
