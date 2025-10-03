"""Views for authentication."""

from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    ChangePasswordSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from .token_manager import TokenManager


def auth_required(
    view_func: Callable[..., HttpResponse],
) -> Callable[..., HttpResponse]:
    """Simple decorator for template views - middleware handles JWT conversion."""

    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        # Redirect to login if not authenticated
        from django.shortcuts import redirect

        return redirect("/login/")

    return wrapper


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """Create a new user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate secure JWT tokens
        tokens = TokenManager.create_tokens(user)

        # Create session for template views
        TokenManager.create_session_from_jwt(request, user)

        return TokenManager.create_secure_response(
            {
                "user": UserProfileSerializer(user).data,
                "message": "User registered successfully.",
            },
            tokens,
        )


class UserLoginView(TokenObtainPairView):
    """View for user login."""

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """Login user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Generate secure JWT tokens
        tokens = TokenManager.create_tokens(user)

        # Create session for template views
        TokenManager.create_session_from_jwt(request, user)

        return TokenManager.create_secure_response(
            {"user": UserProfileSerializer(user).data, "message": "Login successful."},
            tokens,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        """Return the current user."""
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """View for changing password."""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        """Return the current user."""
        return self.request.user

    def update(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """Update user password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def logout_view(request: HttpRequest) -> Response:
    """View for user logout."""
    try:
        # Get refresh token from cookies or request body
        refresh_token = TokenManager.get_refresh_token_from_cookies(
            request
        ) or request.data.get("refresh")

        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        # Logout Django session
        from django.contrib.auth import logout

        logout(request)

        # Clear tokens from cookies
        response = TokenManager.create_secure_response(
            {"message": "Logout successful."}
        )
        response = TokenManager.clear_tokens_from_cookies(response)

        return response
    except Exception:
        # Even if token is invalid, clear cookies and logout
        from django.contrib.auth import logout

        logout(request)

        response = TokenManager.create_secure_response(
            {"message": "Logout successful."}
        )
        response = TokenManager.clear_tokens_from_cookies(response)
        return response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_info_view(request: HttpRequest) -> Response:
    """View to get current user information."""
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def check_auth_view(request: HttpRequest) -> Response:
    """View to check if user is authenticated (supports both JWT and session)."""
    if request.user.is_authenticated:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"detail": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_session_view(request: HttpRequest) -> Response:
    """View to create a Django session from JWT token."""
    # The user is already authenticated via JWT, create a session
    TokenManager.create_session_from_jwt(request, request.user)
    return Response(
        {"message": "Session created successfully"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def refresh_token_view(request: HttpRequest) -> Response:
    """View to refresh access token."""
    refresh_token = TokenManager.get_refresh_token_from_cookies(
        request
    ) or request.data.get("refresh")

    if not refresh_token:
        return Response(
            {"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Try to refresh the token
    new_tokens = TokenManager.refresh_access_token(refresh_token)

    if not new_tokens:
        return Response(
            {"error": "Invalid or expired refresh token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Return new tokens in secure cookies
    return TokenManager.create_secure_response(
        {"message": "Token refreshed successfully."}, new_tokens
    )


def login_page_view(request: HttpRequest) -> HttpResponse:
    """View to serve login page."""
    return render(request, "accounts/login.html")


@auth_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """View for user dashboard."""
    return render(request, "dashboard.html", {"user": request.user})


@auth_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Example protected view - just add @auth_required decorator!"""
    return render(
        request,
        "accounts/dashboard.html",
        {"user": request.user, "page_title": "User Profile"},
    )


@auth_required
def settings_view(request: HttpRequest) -> HttpResponse:
    """Another example protected view."""
    return render(
        request,
        "accounts/dashboard.html",
        {"user": request.user, "page_title": "Settings"},
    )
