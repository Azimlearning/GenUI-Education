"""LangGraph shared state. Mirrors docs/SYSTEM_ARCHITECTURE.md section 4."""

from typing import TypedDict

from schemas.intent import Intent


class PipelineState(TypedDict, total=False):
    session_id: str
    query: str
    intent: Intent | None  # Router output (pydantic)
    canonical_concept: str | None
    cache_key: str | None
    explanation_done: bool
    artifact_plan: dict | None  # ArtifactPlan (Phase 1)
    artifact_code: str | None
    verification_report: dict | None  # VerifierReport (Phase 2)
    retry_count: int  # hard cap 2
    prior_artifact_html: str | None  # set only in modification cycles
    final_artifact_id: str | None
    failure_reason: str | None
