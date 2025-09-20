from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Trade
from .serializers import TradeSerializer
from apps.users.models import User


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        user_id = self.request.query_params.get("user_id")
        symbol = self.request.query_params.get("symbol")
        sold = self.request.query_params.get("sold")

        if self.request.user.role == User.Role.USER:
            if user_id and str(user_id) != str(user.id):
                raise PermissionDenied("You don't have permissions for this action.")
            qs = qs.filter(user_id=user.id)
        else:
            if user_id:
                qs = qs.filter(user_id=user_id)

        if symbol:
            qs = qs.filter(symbol__iexact=symbol)
        if sold is not None:
            qs = qs.filter(sold=(sold.lower() == "true"))

        return qs
