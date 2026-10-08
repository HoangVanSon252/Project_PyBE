"""Small, dependency-free HTTP hardening middleware for a single API instance."""
from collections import defaultdict, deque
from time import monotonic
from secrets import token_urlsafe
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

SAFE = {"GET", "HEAD", "OPTIONS"}

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.hits = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        now = monotonic()
        key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
        bucket = self.hits[key]
        while bucket and now - bucket[0] > settings.RATE_LIMIT_WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= settings.RATE_LIMIT_REQUESTS:
            return JSONResponse({"success": False, "code": "RATE_LIMIT", "message": "Quá nhiều yêu cầu", "data": None}, status_code=429, headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)})
        bucket.append(now)

        if request.method not in SAFE and request.cookies.get("access_token"):
            csrf_cookie = request.cookies.get("csrf_token")
            csrf_header = request.headers.get("X-CSRF-Token")
            if not csrf_cookie or csrf_cookie != csrf_header:
                return JSONResponse({"success": False, "code": "CSRF_FAILED", "message": "CSRF token không hợp lệ", "data": None}, status_code=403)

        response = await call_next(request)
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; object-src 'none'",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        })
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if not request.cookies.get("csrf_token"):
            response.set_cookie("csrf_token", token_urlsafe(32), httponly=False, secure=settings.COOKIE_SECURE, samesite=settings.COOKIE_SAMESITE, path="/")
        return response
