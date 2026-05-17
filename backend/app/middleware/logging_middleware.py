"""
Logging Middleware for FastAPI
Automatically tracks requests with session and request IDs
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Callable
import json

from app.utils.logger import (
    logger,
    set_session_id,
    set_request_id,
    generate_session_id,
    generate_request_id,
    get_session_id,
    get_request_id
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    Tracks sessions and correlates requests end-to-end
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or retrieve session ID from cookie
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = generate_session_id()

        # Generate unique request ID
        request_id = generate_request_id()

        # Set context variables
        set_session_id(session_id)
        set_request_id(request_id)

        # Extract request information
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)

        # Start timing
        start_time = time.time()

        # Log request
        logger.info(
            f"Request started: {method} {path}",
            method=method,
            path=path,
            url=url,
            client_ip=client_host,
            query_params=query_params,
            user_agent=request.headers.get('user-agent', 'unknown')
        )

        # Process request
        response = None
        error = None
        try:
            response = await call_next(request)

            # Set session ID cookie if not present
            if 'session_id' not in request.cookies:
                response.set_cookie(
                    key='session_id',
                    value=session_id,
                    max_age=86400 * 30,  # 30 days
                    httponly=True,
                    samesite='lax'
                )

            # Add tracking headers
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Session-ID'] = session_id

        except Exception as e:
            error = e
            logger.exception(
                f"Request failed: {method} {path}",
                method=method,
                path=path,
                error=str(e)
            )
            raise

        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Log response
            if response:
                logger.info(
                    f"Request completed: {method} {path}",
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_seconds=round(duration, 4),
                    content_length=response.headers.get('content-length', 0)
                )

        return response


class RequestBodyLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request and response bodies
    Use with caution - may log sensitive data
    """

    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_length: int = 1000
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request body if enabled
        if self.log_request_body and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')[:self.max_body_length]
                    try:
                        body_json = json.loads(body_str)
                        logger.debug(
                            f"Request body: {request.method} {request.url.path}",
                            body=body_json
                        )
                    except json.JSONDecodeError:
                        logger.debug(
                            f"Request body (raw): {request.method} {request.url.path}",
                            body=body_str
                        )

                # Re-create request with body for downstream handlers
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive

            except Exception as e:
                logger.warning(f"Failed to log request body: {str(e)}")

        # Process request
        response = await call_next(request)

        return response


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track performance metrics
    """

    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                duration_seconds=round(duration, 4),
                threshold=self.slow_request_threshold
            )

        return response


__all__ = [
    'LoggingMiddleware',
    'RequestBodyLoggingMiddleware',
    'PerformanceLoggingMiddleware'
]
