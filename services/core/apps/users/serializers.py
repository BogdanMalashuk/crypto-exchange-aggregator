from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Profile, ApiKey


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
        )
        user.set_password(validated_data["password"])
        user.save()
        Profile.objects.create(user=user)

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user", "role", "created_at"]


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ["id", "exchange", "api_key", "api_secret", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        profile = self.context["request"].user.profile
        return ApiKey.objects.create(profile=profile, **validated_data)
