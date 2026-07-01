"""`POST /api/ask` — run the pipeline and stream the visible reasoning + composed component.

The frontend POSTs `{ question, student_id? }`; we stream Server-Sent Events:
  - `agent_step`      — one per reasoning step, as each node produces it (drives the pipeline UI)
  - `component_block` — the composed interactive (pattern + props + meta)
  - `done`            — terminal

We use LangGraph's `astream(..., stream_mode="updates")` so each node's steps are emitted as
soon as that node finishes (D-03 — visible reasoning). A small delay between steps keeps the
"thinking" legible in the demo; remove/tune in P4.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.agents.graph import build_graph
from app.models import (
    AgentStep,
    ComponentBlock,
    ComponentEvent,
    DoneEvent,
    ErrorEvent,
    PipelineState,
)
from app.providers.metrics import METRICS
from app.store import due_for_review, get_store

router = APIRouter(prefix="/api", tags=["pipeline"])

# Demo pacing: pause between streamed steps so the pipeline is watchable (seconds).
STEP_DELAY_S = 0.6


class AskRequest(BaseModel):
    question: str
    student_id: str | None = None


class InteractionRequest(BaseModel):
    """An interaction event fed back from a rendered component (P3)."""

    student_id: str
    topic: str
    correct: bool
    misconception_id: str | None = None
    pattern: str | None = None


def _sse(event: BaseModel) -> dict[str, str]:
    """Serialize a Pydantic event model to an sse-starlette event dict."""
    payload = event.model_dump(mode="json")
    return {"event": payload["type"], "data": json.dumps(payload)}


async def _event_stream(req: AskRequest) -> AsyncIterator[dict[str, str]]:
    graph = build_graph()
    initial = PipelineState(question=req.question, student_id=req.student_id)

    try:
        async for chunk in graph.astream(initial, stream_mode="updates"):
            # chunk == { node_name: { partial update dict } }
            for update in chunk.values():
                for raw_step in update.get("steps", []) or []:
                    step = raw_step if isinstance(raw_step, AgentStep) else AgentStep.model_validate(raw_step)
                    yield _sse(step)
                    await asyncio.sleep(STEP_DELAY_S)

                block = update.get("block")
                if block is not None:
                    block_model = block if isinstance(block, ComponentBlock) else ComponentBlock.model_validate(block)
                    yield _sse(ComponentEvent(block=block_model))
        yield _sse(DoneEvent())
    except Exception as exc:  # noqa: BLE001 - surface any pipeline error to the client
        yield _sse(ErrorEvent(message=str(exc)))


@router.post("/ask")
async def ask(req: AskRequest) -> EventSourceResponse:
    return EventSourceResponse(_event_stream(req))


@router.get("/metrics")
async def metrics() -> dict:
    """Per-LLM-call observability for the dev panel (provider, tokens, cost, latency)."""
    return {"summary": METRICS.summary(), "recent": METRICS.recent(limit=25)}


def _profile_payload(student_id: str) -> dict:
    profile = get_store().get(student_id)
    return {
        "student_id": student_id,
        "mastery": profile.mastery,
        "misconceptions": [
            {
                "misconception_id": o.misconception_id,
                "topic": o.topic,
                "resolved": o.resolved,
                "review_due": o.review_due.isoformat() if o.review_due else None,
            }
            for o in profile.misconceptions.values()
        ],
        "due_now": [o.misconception_id for o in due_for_review(profile)],
    }


@router.post("/interaction")
async def interaction(req: InteractionRequest) -> dict:
    """Close the loop (P3): a component reports how the learner did; update mastery + review."""
    get_store().record_interaction(
        req.student_id, req.topic, req.correct, misconception_id=req.misconception_id
    )
    return _profile_payload(req.student_id)


@router.get("/profile/{student_id}")
async def profile(student_id: str) -> dict:
    """The learner model: mastery per topic + misconceptions + what's due for review."""
    return _profile_payload(student_id)


@router.get("/teacher")
async def teacher() -> dict:
    """Teacher dashboard feed (B2B2C wedge): every learner's mastery + misconceptions + reviews."""
    students = [_profile_payload(sid) for sid in get_store().student_ids()]
    return {"students": students}
