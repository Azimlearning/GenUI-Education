"""Runtime settings, loaded from environment / `.env`."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    frontend_origin: str = "http://localhost:3000"

    # Provider keys (optional until P1). The router treats an empty key as "not configured"
    # and falls through to the next provider / the scripted stub.
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""

    # Learner store (D-11): "memory" (default) | "sqlite"
    learner_store: str = "memory"
    learner_store_path: str = "./synapse.sqlite3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
