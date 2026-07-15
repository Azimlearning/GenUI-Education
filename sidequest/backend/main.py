"""Axiom FastAPI application entrypoint."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.ask import router as ask_router
from config import get_settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

settings = get_settings()

app = FastAPI(title="Axiom API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "llm": "live" if settings.llm_enabled else "echo"}


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # API_SPEC.md section 1: errors follow {error: {code, message, retryable}}.
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_request",
                "message": str(exc.errors()[0]["msg"]) if exc.errors() else "invalid request",
                "retryable": False,
            }
        },
    )


@app.middleware("http")
async def vendor_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/vendor/"):
        # Pinned, immutable libraries (API_SPEC.md: immutable cache headers).
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response


vendor_dir = Path(settings.vendor_dir)
if vendor_dir.is_dir():
    app.mount("/vendor", StaticFiles(directory=vendor_dir), name="vendor")
else:  # pragma: no cover - misconfiguration guard
    logging.getLogger(__name__).warning("vendor dir missing: %s", vendor_dir)
