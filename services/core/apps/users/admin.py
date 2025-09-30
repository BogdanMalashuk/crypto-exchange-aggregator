from django.contrib import admin
from .models import User, ApiKey


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username")


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "exchange", "created_at")
    list_filter = ("exchange",)
