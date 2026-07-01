"""Synapse backend entrypoint — FastAPI app.

Run: `uv run uvicorn app.main:app --reload --port 8000`
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import router as api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Synapse",
    version=__version__,
    description="Visible multi-agent pedagogical pipeline for KSSM SPM science.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "synapse-backend", "version": __version__}
