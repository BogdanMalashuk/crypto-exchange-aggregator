from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("apps.users.urls")),
    path('trades/', include("apps.trades.urls")),
    path('reports/', include("apps.reports.urls")),
]
