import time
import asyncio
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.core.config import settings

# key -> (window_start_epoch, count)
_BUCKET: Dict[str, Tuple[int, int]] = {}
_LOCK = asyncio.Lock()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit fijo por minuto, por API key + path, solo /api/*."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        api_key = request.headers.get("x-api-key", "")
        limit = settings.rate_limit_per_minute
        now = int(time.time())
        window = now - (now % 60)
        key = f"{api_key}:{request.url.path}"

        async with _LOCK:
            wstart, count = _BUCKET.get(key, (window, 0))
            if wstart != window:
                wstart, count = window, 0
            if count >= limit:
                retry_after = 60 - (now - wstart)
                return JSONResponse(
                    status_code=429,
                    content={"status": "error", "error": {"code": "RATE_LIMITED", "message": "Rate limit excedido", "details": None}},
                    headers={
                        "RateLimit-Limit": str(limit),
                        "RateLimit-Remaining": "0",
                        "Retry-After": str(max(1, retry_after)),
                    },
                )
            count += 1
            _BUCKET[key] = (wstart, count)

        response: Response = await call_next(request)
        response.headers["RateLimit-Limit"] = str(limit)
        response.headers["RateLimit-Remaining"] = str(max(0, limit - count))
        return response