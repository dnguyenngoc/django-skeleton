"""Serializers for authentication."""

from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:  # noqa: D106
        """Meta class for UserRegistrationSerializer."""

        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate password confirmation."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Password fields don't match."}
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create a new user."""
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate user credentials."""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), username=email, password=password
            )

            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            if user.deleted_at:
                raise serializers.ValidationError("User account has been deleted.")

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    full_name = serializers.ReadOnlyField()

    class Meta:  # noqa: D106
        """Meta class for UserProfileSerializer."""

        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "email", "created_at", "updated_at")


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value: str) -> str:
        """Validate old password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate password confirmation."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Password fields don't match."}
            )
        return attrs

    def save(self, **kwargs: Any) -> User:
        """Save new password."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with secure claims."""

    @classmethod
    def get_token(cls, user: User) -> RefreshToken:
        """Create token with secure claims - NO PASSWORD INFO."""
        token = super().get_token(user)

        # Add custom claims - only safe user info
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["is_active"] = user.is_active
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser

        # DO NOT include password or sensitive info
        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate credentials and return tokens."""
        data = super().validate(attrs)

        # Add user info to response (without password)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "full_name": self.user.full_name,
            "phone": self.user.phone,
            "is_active": self.user.is_active,
            "created_at": self.user.created_at,
            "updated_at": self.user.updated_at,
        }

        return data
