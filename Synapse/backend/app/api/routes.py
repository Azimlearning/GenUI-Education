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

router = APIRouter(prefix="/api", tags=["pipeline"])

# Demo pacing: pause between streamed steps so the pipeline is watchable (seconds).
STEP_DELAY_S = 0.6


class AskRequest(BaseModel):
    question: str
    student_id: str | None = None


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
