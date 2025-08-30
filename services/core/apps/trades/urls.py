from django.urls import path
from .views import lots_view, deactivate_lot, trades_list

urlpatterns = [
    path("lots/", lots_view, name="purchase_lots"),
    path("lots/<int:lot_id>/deactivate/", deactivate_lot, name="deactivate_purchase_lot"),
    path("", trades_list, name="trades_list"),
]
