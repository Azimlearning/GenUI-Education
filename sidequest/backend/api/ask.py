"""POST /api/ask: run the pipeline, stream typed SSE events.

The API layer owns the wire format; graph nodes emit typed payloads into an
asyncio queue via the RunContext and this module serializes them in order.
Ordering guarantees (API_SPEC.md section 2): meta first, done last.
"""

import asyncio
import logging
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from graph.build import build_graph
from graph.context import RunContext
from schemas.events import DonePayload, TextDeltaPayload, Timings, format_sse
from services.background import spawn
from services.messages import ensure_session, save_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

_SENTINEL = None

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # never buffer the stream behind a proxy
}


class AskRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    # Oversized/degenerate input (hostile case H5) is rejected here,
    # before any LLM spend. Limit mirrors config.max_query_chars.
    message: str = Field(min_length=1, max_length=2000)


async def _event_stream(req: AskRequest) -> AsyncIterator[str]:
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    queue: asyncio.Queue = asyncio.Queue()

    async def emit(payload: BaseModel) -> None:
        await queue.put(payload)

    ctx = RunContext(run_id=run_id, session_id=req.session_id, emit=emit)

    # Persistence is off the critical path: chat must stream even if the
    # database is slow or down (failures are logged inside the services).
    # One sequential chain per turn so the session row exists before the
    # message rows reference it.
    async def persist_turn(get_explanation) -> None:
        await ensure_session(req.session_id)
        await save_message(req.session_id, "user", req.message)
        explanation = await get_explanation()
        if explanation:
            await save_message(req.session_id, "assistant", explanation)

    explanation_ready: asyncio.Future[str] = asyncio.get_running_loop().create_future()

    async def get_explanation() -> str:
        return await explanation_ready

    spawn(persist_turn(get_explanation), name=f"persist:{run_id}")

    async def run_pipeline() -> None:
        try:
            await build_graph().ainvoke(
                {"session_id": req.session_id, "query": req.message, "retry_count": 0},
                config={"configurable": {"ctx": ctx}},
            )
        except Exception:
            logger.exception("pipeline failed (run_id=%s)", run_id)
        finally:
            await queue.put(_SENTINEL)

    task = asyncio.create_task(run_pipeline())

    event_id = 0
    explanation_parts: list[str] = []
    try:
        while True:
            payload = await queue.get()
            if payload is _SENTINEL:
                break
            if isinstance(payload, TextDeltaPayload):
                explanation_parts.append(payload.chunk)
            event_id += 1
            yield format_sse(payload, event_id)

        done = DonePayload(
            usage=ctx.usage,
            timings_ms=Timings(first_token=ctx.first_token_ms or 0, artifact_total=0),
        )
        event_id += 1
        yield format_sse(done, event_id)
    finally:
        # Hand the final text to the background persistence chain; on abort
        # this resolves with whatever streamed before the disconnect.
        if not explanation_ready.done():
            explanation_ready.set_result("".join(explanation_parts))
        if not task.done():
            task.cancel()


@router.post("/ask")
async def ask(req: AskRequest) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(req), media_type="text/event-stream", headers=SSE_HEADERS
    )
