from django.contrib import admin
from .models import User, Profile, ApiKey


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "created_at")
    list_filter = ("role",)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "exchange", "created_at")
    list_filter = ("exchange",)
