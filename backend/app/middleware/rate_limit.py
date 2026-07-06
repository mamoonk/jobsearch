import time
from collections import defaultdict

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.buckets: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/api/v1/alignments", "/api/v1/cover-letters", "/api/v1/interview-prep")):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            self.buckets[client_ip] = [
                t for t in self.buckets[client_ip]
                if now - t < self.window_seconds
            ]
            if len(self.buckets[client_ip]) >= self.max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            self.buckets[client_ip].append(now)

        return await call_next(request)
