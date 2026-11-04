"""
app/middleware/rate_limit.py
Implementasi rate limiting ringan berbasis in-memory sliding window.
Tidak memerlukan dependensi eksternal (slowapi / redis).
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware sliding window rate limiter berbasis IP.
    
    Aturan per-endpoint (max_requests, window_seconds):
    - Endpoint komputasi berat (CRISPR scan, DMS): 30 req/menit
    - Endpoint analisis mutasi: 60 req/menit
    - Endpoint read-only (catalog, targets): 200 req/menit
    - Default: 120 req/menit
    """

    ROUTE_LIMITS: Dict[str, tuple] = {
        "/api/v1/crispr/find-targets":            (30, 60),
        "/api/v1/crispr/design-for-gene":         (20, 60),
        "/api/v1/phytoai/dreb2a/dms-scan":        (20, 60),
        "/api/v1/phytoai/dreb2a/predict-mutation": (60, 60),
        "/api/v1/phytoai/assess-coordinates":     (60, 60),
        "/api/v1/sequences":                       (30, 60),
    }
    DEFAULT_LIMIT = (120, 60)  # 120 req / 60 detik untuk semua endpoint lainnya

    def __init__(self, app):
        super().__init__(app)
        self._windows: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _get_client_ip(self, request: Request) -> str:
        """Ambil IP klien; mendukung X-Forwarded-For dari reverse proxy."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_limit(self, path: str) -> tuple:
        """Tentukan limit berdasarkan prefix path endpoint."""
        for route_prefix, limit in self.ROUTE_LIMITS.items():
            if path.startswith(route_prefix):
                return limit
        return self.DEFAULT_LIMIT

    async def dispatch(self, request: Request, call_next):
        # Jangan rate-limit endpoint health check & static files
        path = request.url.path
        if path in ("/health", "/", "/docs", "/redoc", "/openapi.json") or path.startswith("/static/"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        max_requests, window_sec = self._get_limit(path)
        now = time.monotonic()
        window_start = now - window_sec
        key = f"{client_ip}:{path}"

        async with self._lock:
            dq = self._windows[key]
            # Hapus entri di luar jendela sliding window
            while dq and dq[0] < window_start:
                dq.popleft()

            if len(dq) >= max_requests:
                oldest = dq[0]
                retry_after = max(1, int(window_sec - (now - oldest)) + 1)
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": (
                            f"Terlalu banyak permintaan. Batas {max_requests} per {window_sec}s "
                            f"untuk endpoint ini. Coba lagi dalam {retry_after} detik."
                        ),
                        "limit": max_requests,
                        "window_seconds": window_sec,
                        "retry_after_seconds": retry_after,
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Window": str(window_sec),
                    },
                )

            dq.append(now)
            remaining = max_requests - len(dq)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(window_sec)
        return response

