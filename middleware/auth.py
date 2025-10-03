"""Authentication middleware for JWT to session conversion."""

from collections.abc import Callable

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTSessionMiddleware:
    """Middleware to automatically create Django sessions from JWT tokens."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and create session from JWT if needed."""
        # Only process if user is not already authenticated
        if not request.user.is_authenticated:
            # Check for JWT token in Authorization header
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                try:
                    jwt_auth = JWTAuthentication()
                    user, validated_token = jwt_auth.authenticate(request)
                    if user and user.is_authenticated:
                        # Create a session for this user
                        login(request, user)
                except Exception:
                    # JWT authentication failed, continue without session
                    pass

        response = self.get_response(request)
        return response
