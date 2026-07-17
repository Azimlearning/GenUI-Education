"""Central configuration: budgets, model ids, timeouts, rate limits.

Values come from the environment (.env in local dev, real env in deploy).
See docs/TECHNICAL.md section 3 for the canonical variable list.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

# USD per million tokens (input, output). Used for per-run cost tracing.
MODEL_PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-5": (3.00, 15.00),
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""
    database_url: str = "postgresql+asyncpg://axiom:axiom@localhost:5432/axiom"

    # Generator, Verifier, Planner run on strong; Router, Explainer, Tutor on fast.
    model_strong: str = "claude-sonnet-5"
    model_fast: str = "claude-haiku-4-5-20251001"

    max_run_cost_usd: float = 0.75
    # The founding brief said 30s. Measured reality: a complete artifact is
    # 3-9k output tokens, provider time-to-first-token varies up to ~100s on
    # cold prompts, and a verifier-driven revision adds a full cycle. 420s is
    # the hard pathological cap; the branch degrades early instead of starting
    # a revision with < 90s of runway (see graph/nodes/artifact.py). The
    # staged progress card is the UX answer, and the text branch is never
    # blocked by this timeout either way. PLANNING.md findings 7 and 12.
    artifact_timeout_s: int = 420
    gen_rate_limit_per_hour: int = 10

    # Incident switch (SECURITY.md section 7): forces text-only mode app-wide.
    artifacts_disabled: bool = False

    # ``shadow`` observes the full Keras model while the LLM stays authoritative.
    # ``local`` is reserved for the later confidence-gated rollout.
    router_mode: Literal["llm", "shadow", "local"] = "llm"
    router_model_dir: Path = REPO_ROOT / "ml" / "router-distill" / "out"

    # When true (or when no API key is set) the pipeline runs without LLM calls,
    # echoing the query back. Keeps `make dev` working from a clean clone.
    echo_mode: bool = False

    vendor_dir: str = str(REPO_ROOT / "vendor")
    cors_origins: list[str] = ["http://localhost:3000"]

    # Public origin of the app as the browser sees it. Injected into every
    # artifact's CSP so vendored /vendor/* scripts load inside the
    # opaque-origin srcdoc iframe (SECURITY.md section 2.3).
    public_origin: str = "http://localhost:3000"

    # Post-processor rejects artifacts larger than this (TECHNICAL.md budgets).
    max_artifact_bytes: int = 200_000

    max_query_chars: int = 2000  # H5 hostile case: oversized input rejected pre-LLM

    @property
    def llm_enabled(self) -> bool:
        return bool(self.anthropic_api_key) and not self.echo_mode

    def price_for(self, model: str) -> tuple[float, float]:
        return MODEL_PRICES_PER_MTOK.get(model, (0.0, 0.0))


@lru_cache
def get_settings() -> Settings:
    return Settings()
