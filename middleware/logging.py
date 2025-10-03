"""Logging middleware for request/response logging."""

import logging
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Log all requests and responses for debugging."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Log request and response."""
        # Log request
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
        )

        response = self.get_response(request)

        # Log response
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.path}"
        )

        return response
