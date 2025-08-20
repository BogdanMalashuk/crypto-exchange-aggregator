from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "status", "format", "created_at")
    list_filter = ("status", "format")
