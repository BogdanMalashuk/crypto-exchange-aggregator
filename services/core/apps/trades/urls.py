from .views import TradeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', TradeViewSet)

urlpatterns = router.urls

