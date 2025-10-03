"""Token management utilities for secure JWT handling."""

from typing import Any

from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class TokenManager:
    """Secure token management for JWT authentication."""

    @staticmethod
    def create_tokens(user: AbstractUser) -> dict[str, str]:
        """Create access and refresh tokens for user."""
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def set_tokens_in_cookies(
        response: HttpResponse, tokens: dict[str, str]
    ) -> HttpResponse:
        """Set JWT tokens in secure HTTP-only cookies."""
        # Access token - short lived, httpOnly
        response.set_cookie(
            "access_token",
            tokens["access"],
            max_age=15 * 60,  # 15 minutes
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="Strict",
            path="/",
        )

        # Refresh token - longer lived, httpOnly
        response.set_cookie(
            "refresh_token",
            tokens["refresh"],
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="Strict",
            path="/",
        )

        return response

    @staticmethod
    def clear_tokens_from_cookies(response: HttpResponse) -> HttpResponse:
        """Clear JWT tokens from cookies."""
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response

    @staticmethod
    def get_token_from_cookies(request: HttpRequest) -> str | None:
        """Get access token from cookies."""
        return request.COOKIES.get("access_token")

    @staticmethod
    def get_refresh_token_from_cookies(request: HttpRequest) -> str | None:
        """Get refresh token from cookies."""
        return request.COOKIES.get("refresh_token")

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict[str, str] | None:
        """Refresh access token using refresh token."""
        try:
            refresh = RefreshToken(refresh_token)
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),  # New refresh token (rotated)
            }
        except Exception:
            return None

    @staticmethod
    def create_session_from_jwt(request: HttpRequest, user: AbstractUser) -> None:
        """Create Django session from JWT authentication."""
        from django.contrib.auth import login

        login(request, user)

    @staticmethod
    def create_secure_response(
        data: dict[str, Any], tokens: dict[str, str] | None = None
    ) -> Response:
        """Create secure response with optional token cookies."""
        response = Response(data)

        if tokens:
            response = TokenManager.set_tokens_in_cookies(response, tokens)

        # Security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
