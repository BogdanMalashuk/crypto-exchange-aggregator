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

    @action(detail=True, methods=["post"])
    def mark_sold(self, request, pk=None):
        trade = self.get_object()
        if trade.sold:
            return Response({"detail": "Trade already sold"}, status=status.HTTP_400_BAD_REQUEST)
        trade.sold = True
        trade.sold_at = timezone.now()
        trade.save()
        return Response({"detail": "Trade marked as sold"})
