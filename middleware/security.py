"""Security middleware for additional protection."""

from typing import Any

from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Add security headers to all responses."""
    
    def __init__(self, get_response: Any) -> None:
        """Initialize middleware."""
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Add security headers to response."""
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response