from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.db import init_db
from app.api.routes import router as api_router
from app.api.ws import ws_router
from app.middleware.rate_limit import RateLimitMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Nequi Chat Backend", version="0.1.0")

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        detail = getattr(exc, "detail", None)
        if isinstance(detail, dict) and "code" in detail:
            payload = {"status": "error", "error": detail}
        else:
            payload = {"status": "error", "error": {"code": "HTTP_EXCEPTION", "message": str(detail), "details": None}}
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": {"code": "SERVER_ERROR", "message": "Error del servidor", "details": str(exc)}},
        )

    @app.on_event("startup")
    def _on_startup():
        init_db()

    # Rate limit para /api/*
    app.add_middleware(RateLimitMiddleware)

    # Routers
    app.include_router(api_router, tags=["messages"])
    app.include_router(ws_router, tags=["ws"])
    return app

app = create_app()