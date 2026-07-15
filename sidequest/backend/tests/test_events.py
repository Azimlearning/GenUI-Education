"""Wire-format tests for the typed SSE protocol (API_SPEC.md section 2).

These shapes are mirrored by frontend/types/events.ts; changing one side
must break a test until the other side is updated too.
"""

import json

from schemas.events import (
    EVENT_NAMES,
    ArtifactDonePayload,
    ArtifactFailedPayload,
    ArtifactStatusPayload,
    DonePayload,
    MetaPayload,
    TextDeltaPayload,
    TextDonePayload,
    Timings,
    Usage,
    format_sse,
)
from schemas.intent import Intent


def make_meta() -> MetaPayload:
    intent = Intent(
        artifact_type="simulation",
        domain="physics",
        complexity=2,
        canonical_concept="projectile_motion",
    )
    return MetaPayload(intent=intent.public, canonical_concept="projectile_motion", cache="miss")


def test_all_protocol_events_are_registered():
    assert set(EVENT_NAMES.values()) == {
        "meta",
        "text_delta",
        "text_done",
        "artifact_status",
        "artifact_delta",
        "artifact_done",
        "artifact_failed",
        "tutor_msg",
        "done",
    }


def test_format_sse_frame_shape():
    frame = format_sse(TextDeltaPayload(chunk="hello"), event_id=3)
    assert frame == 'id: 3\nevent: text_delta\ndata: {"chunk":"hello"}\n\n'


def test_meta_payload_matches_spec_example():
    data = json.loads(make_meta().model_dump_json())
    assert data == {
        "intent": {"artifact_type": "simulation", "domain": "physics", "complexity": 2},
        "canonical_concept": "projectile_motion",
        "cache": "miss",
    }


def test_done_payload_shape():
    data = json.loads(DonePayload(usage=Usage(), timings_ms=Timings()).model_dump_json())
    assert data == {
        "usage": {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0},
        "timings_ms": {"first_token": 0, "artifact_total": 0},
    }


def test_text_done_is_empty_object():
    assert TextDonePayload().model_dump_json() == "{}"


def test_artifact_event_shapes():
    status = json.loads(ArtifactStatusPayload(stage="planning").model_dump_json())
    assert status == {"stage": "planning"}

    done = json.loads(
        ArtifactDonePayload(artifact_id="art_9f3c", title="T", html="<html/>").model_dump_json()
    )
    assert set(done) == {"artifact_id", "title", "html"}

    failed = json.loads(
        ArtifactFailedPayload(
            reason="verification_failed", detail_user="honest copy", retryable=True
        ).model_dump_json()
    )
    assert set(failed) == {"reason", "detail_user", "retryable"}
