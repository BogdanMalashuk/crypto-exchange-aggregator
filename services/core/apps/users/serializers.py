from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Profile, ApiKey
from .crypto import encrypt_text, decrypt_text
from django.db import IntegrityError


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
    api_secret = serializers.CharField(write_only=True)

    class Meta:
        model = ApiKey
        fields = ["id", "exchange", "api_key", "api_secret", "created_at"]
        read_only_fields = ["id", "created_at"]

    @staticmethod
    def get_api_secret_masked(self, obj) -> str:
        secret = decrypt_text(obj.api_secret)
        return ("***" + secret[-4:]) if secret else "***"

    def create(self, validated_data):
        request = self.context["request"]
        profile = request.user.profile

        raw_secret = validated_data.pop("api_secret")
        encrypted_secret = encrypt_text(raw_secret)

        try:
            instance = ApiKey.objects.create(
                profile=profile,
                api_secret=encrypted_secret,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"exchange": "API key for this exchange already exists for your profile."}
            )
        return instance

    def update(self, instance, validated_data):
        if "api_secret" in validated_data:
            instance.api_secret = encrypt_text(validated_data.pop("api_secret"))
        for field in ("exchange", "api_key"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
