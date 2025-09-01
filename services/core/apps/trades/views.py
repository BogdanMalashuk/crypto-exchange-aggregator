from rest_framework.views import APIView
from .models import Trade, Lot
from packages.common.kafka.producer import publish_event
from packages.common.kafka.events import TradeCreatedEvent
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .utils.inventory import active_lots
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


class TradeCreateView(APIView):
    def post(self, request):
        profile = request.user.profile
        exchange = request.data["exchange"]
        symbol = request.data["symbol"]
        side = request.data["side"]
        amount = Decimal(request.data["amount"])
        price = Decimal(request.data["price"])
        timestamp = request.data.get("timestamp") or timezone.now()

        lot_id = request.data.get("lot_id")
        lot = None
        if lot_id:
            from .models import Lot
            try:
                lot = Lot.objects.get(id=lot_id)
            except Lot.DoesNotExist:
                lot = None

        trade = Trade.objects.create(
            profile=profile,
            exchange=exchange,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            timestamp=timestamp,
            purchase_lot=lot
        )

        buy_price = lot.buy_price if lot else price
        current_price = price
        event = TradeCreatedEvent.from_trade(
            profile_id=profile.id,
            exchange=exchange,
            symbol=symbol,
            amount=float(amount),
            buy_price=float(buy_price),
            current_price=float(current_price)
        )

        publish_event("trade.created", event.to_dict())

        return Response({"id": trade.id})


@api_view(["GET"])
@permission_classes([AllowAny])
def lots_view(request):
    data = active_lots()
    return Response(data)


@require_POST
def deactivate_lot(request, lot_id):
    lot = get_object_or_404(Lot, pk=lot_id, is_active=True)
    lot.is_active = False
    lot.save(update_fields=["is_active"])
    return JsonResponse({
        "status": "success",
        "lot_id": lot.id,
        "is_active": lot.is_active
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trades_list(request):
    profile = request.user.profile
    trades = Trade.objects.filter(profile=profile).order_by("-timestamp")

    data = [
        {
            "id": t.id,
            "exchange": t.exchange,
            "symbol": t.symbol,
            "side": t.side,
            "amount": str(t.amount),
            "price": str(t.price),
            "profit": str(t.profit) if t.profit is not None else None,
            "timestamp": t.timestamp.isoformat(),
        }
        for t in trades
    ]
    return JsonResponse(data, safe=False)
