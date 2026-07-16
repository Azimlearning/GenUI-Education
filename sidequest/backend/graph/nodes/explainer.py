"""Explainer node: stream the text explanation immediately.

Fast model. In later phases this runs in parallel with the artifact branch
and is never blocked by it. Streams text_delta events through the run
context, then text_done.
"""

import asyncio
import logging
import time

from langchain_core.runnables import RunnableConfig

from config import get_settings
from graph.context import get_ctx
from graph.state import PipelineState
from schemas.events import TextDeltaPayload, TextDonePayload
from services.llm import get_llm
from services.prompts import load_prompt, prompt_version
from services.traces import record_trace

logger = logging.getLogger(__name__)


async def explainer_node(state: PipelineState, config: RunnableConfig) -> PipelineState:
    ctx = get_ctx(config)
    settings = get_settings()
    started = time.monotonic()

    model: str | None = None
    tokens_in = tokens_out = 0
    cost = 0.0
    error: str | None = None

    async def emit_chunk(chunk: str) -> None:
        ctx.mark_first_token()
        await ctx.emit(TextDeltaPayload(chunk=chunk))

    if not settings.llm_enabled:
        logger.warning("ECHO MODE: no ANTHROPIC_API_KEY; explainer echoing the query")
        echo = (
            "Echo mode: the backend has no ANTHROPIC_API_KEY configured, so this is "
            f"the walking skeleton talking. You asked: \"{state['query']}\". "
            "Set the key in .env and restart to get real explanations."
        )
        for word in echo.split(" "):
            await emit_chunk(word + " ")
            await asyncio.sleep(0.02)  # visible streaming in the UI
    else:
        model = settings.model_fast
        # Phase 0: the artifact branch does not exist yet, so never promise one.
        # Phase 1 will set this from intent.artifact_type != "text_only".
        artifact_coming = False
        user = (
            f"Question: {state['query']}\n\n"
            f"An interactive artifact {'IS' if artifact_coming else 'is NOT'} "
            "being built for this question."
        )
        try:
            result = await get_llm().stream(
                model=model,
                system=load_prompt("explainer"),
                user=user,
                max_tokens=1024,
                on_chunk=emit_chunk,
            )
            tokens_in, tokens_out, cost = result.tokens_in, result.tokens_out, result.cost_usd
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            logger.exception("explainer stream failed")
            await emit_chunk(
                "Sorry, I hit a problem generating the explanation. Please try again."
            )

    ctx.add_usage(tokens_in, tokens_out, cost)
    await ctx.emit(TextDonePayload())
    record_trace(
        run_id=ctx.run_id,
        session_id=ctx.session_id,
        node="explainer",
        model=model,
        prompt_version=prompt_version("explainer") if model else None,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost,
        latency_ms=int((time.monotonic() - started) * 1000),
        error=error,
    )
    return {"explanation_done": True}
