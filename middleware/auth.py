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
            # Check for JWT token in cookies first
            access_token = request.COOKIES.get("access_token")
            print("🔍 JWT Middleware: User not authenticated, checking cookies...")
            print(f"🔍 Access token in cookies: {'Yes' if access_token else 'No'}")

            if access_token:
                try:
                    # Create a mock request with Authorization header for JWT auth
                    mock_request = request
                    mock_request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

                    jwt_auth = JWTAuthentication()
                    user, validated_token = jwt_auth.authenticate(mock_request)
                    if user and user.is_authenticated:
                        # Create a session for this user
                        login(request, user)
                        print(
                            f"✅ JWT Middleware: Session created for user {user.email}"
                        )
                    else:
                        print("❌ JWT Middleware: JWT authentication failed")
                except Exception as e:
                    # JWT authentication failed, continue without session
                    print(f"❌ JWT Middleware: Exception during JWT auth: {e}")
                    pass
            else:
                print("❌ JWT Middleware: No access token in cookies")
                # Fallback: Check for JWT token in Authorization header
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                if auth_header.startswith("Bearer "):
                    try:
                        jwt_auth = JWTAuthentication()
                        user, validated_token = jwt_auth.authenticate(request)
                        if user and user.is_authenticated:
                            # Create a session for this user
                            login(request, user)
                            email = user.email
                            print(f"✅ JWT Middleware: Session from header for {email}")
                    except Exception as e:
                        # JWT authentication failed, continue without session
                        print(
                            f"❌ JWT Middleware: Exception during header JWT auth: {e}"
                        )
                        pass
        else:
            print(
                f"✅ JWT Middleware: User already authenticated: {request.user.email}"
            )

        response = self.get_response(request)
        return response
