"""Typed SSE event payloads.

This module is the backend half of the protocol contract. It must stay
mirrored with frontend/types/events.ts (API_SPEC.md section 2). The schema
snapshot test in tests/test_events.py guards the wire shapes.
"""

from typing import Literal

from pydantic import BaseModel

from schemas.intent import IntentPublic

ArtifactStage = Literal["planning", "generating", "verifying", "revising", "postprocessing"]


class MetaPayload(BaseModel):
    intent: IntentPublic
    canonical_concept: str
    cache: Literal["hit", "miss"]


class TextDeltaPayload(BaseModel):
    chunk: str


class TextDonePayload(BaseModel):
    pass


class ArtifactStatusPayload(BaseModel):
    stage: ArtifactStage


class ArtifactDeltaPayload(BaseModel):
    chunk: str


class ArtifactDonePayload(BaseModel):
    artifact_id: str
    title: str
    html: str


class ArtifactFailedPayload(BaseModel):
    reason: str
    detail_user: str
    retryable: bool


class TutorMsgPayload(BaseModel):
    text: str


class Usage(BaseModel):
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0


class Timings(BaseModel):
    first_token: int = 0
    artifact_total: int = 0


class DonePayload(BaseModel):
    usage: Usage
    timings_ms: Timings


# Wire name for each payload type. `meta` is always first, `done` always last.
EVENT_NAMES: dict[type[BaseModel], str] = {
    MetaPayload: "meta",
    TextDeltaPayload: "text_delta",
    TextDonePayload: "text_done",
    ArtifactStatusPayload: "artifact_status",
    ArtifactDeltaPayload: "artifact_delta",
    ArtifactDonePayload: "artifact_done",
    ArtifactFailedPayload: "artifact_failed",
    TutorMsgPayload: "tutor_msg",
    DonePayload: "done",
}


def event_name(payload: BaseModel) -> str:
    try:
        return EVENT_NAMES[type(payload)]
    except KeyError as exc:  # pragma: no cover - programming error, not runtime input
        raise TypeError(
            f"{type(payload).__name__} is not a registered SSE payload"
        ) from exc


def format_sse(payload: BaseModel, event_id: int) -> str:
    """Encode one event as an SSE frame with a monotonic id for future resume."""
    data = payload.model_dump_json()
    return f"id: {event_id}\nevent: {event_name(payload)}\ndata: {data}\n\n"
