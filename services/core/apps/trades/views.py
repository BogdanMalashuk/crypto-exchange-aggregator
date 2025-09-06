from .models import Trade
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import viewsets, status
from .serializers import TradeSerializer


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        symbol = self.request.query_params.get("symbol")
        sold = self.request.query_params.get("sold")
        if user_id:
            qs = qs.filter(user_id=user_id)
        if symbol:
            qs = qs.filter(symbol__iexact=symbol)
        if sold is not None:
            qs = qs.filter(sold=(sold.lower() == "true"))
        return qs
