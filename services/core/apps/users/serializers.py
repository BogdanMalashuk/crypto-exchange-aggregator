from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, ApiKey
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
            role=User.Role.USER,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "password"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ApiKeySerializer(serializers.ModelSerializer):
    api_secret = serializers.CharField(write_only=True)
    api_secret_masked = serializers.SerializerMethodField()

    class Meta:
        model = ApiKey
        fields = ["id", "exchange", "api_key", "api_secret", "api_secret_masked"]
        read_only_fields = ["id", "created_at", "api_secret_masked"]

    def get_api_secret_masked(self, obj) -> str:
        secret = decrypt_text(obj.api_secret)
        return ("***" + secret[-4:]) if secret else "***"

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        raw_secret = validated_data.pop("api_secret")
        encrypted_secret = encrypt_text(raw_secret)
        try:
            instance = ApiKey.objects.create(
                user=user,
                api_secret=encrypted_secret,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"exchange": "API key for this exchange already exists for your user."}
            )
        return instance

    def update(self, instance, validated_data):
        if "api_secret" in validated_data:
            instance.api_secret = encrypt_text(validated_data.pop("api_secret"))
        for field in ("exchange", "api_key"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"exchange": "API key for this exchange already exists for your user."}
            )
        return instance
