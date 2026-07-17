"""Generator: the Tier 3 core. Strong model, high max tokens.

Prompt-injection posture (SECURITY.md section 5): the Generator never sees the
raw user question. Its entire input is the ArtifactPlan JSON, plus verifier
issues on a revision pass. Free text can only reach it through the plan's
typed, length-capped fields.
"""

import logging
import time

from config import get_settings
from graph.context import RunContext
from graph.errors import NodeError
from schemas.events import ArtifactDeltaPayload
from schemas.plan import ArtifactPlan
from services.llm import get_llm
from services.prompts import load_prompt, prompt_version
from services.traces import record_trace

logger = logging.getLogger(__name__)

MAX_GENERATOR_TOKENS = 16_000


async def run_generator(
    ctx: RunContext,
    plan: ArtifactPlan,
    revision_issues: list[str] | None = None,
    retry_index: int = 0,
) -> str:
    settings = get_settings()
    model = settings.model_strong
    started = time.monotonic()

    user = "Input plan:\n\n" + plan.model_dump_json(indent=2)
    if revision_issues:
        user += (
            "\n\nREVISION REQUEST. The previous document failed verification. "
            "Fix every issue and output the complete corrected document:\n- "
            + "\n- ".join(revision_issues)
        )

    # Streaming, not create(): long non-streaming requests can be held/stalled
    # server-side (observed: 22s streamed vs 77s+ non-streaming). When the
    # client opted in, chunks flow out as artifact_delta for the
    # build-progress code preview (API_SPEC.md section 2).
    async def on_chunk(chunk: str) -> None:
        if ctx.artifact_delta_enabled:
            await ctx.emit(ArtifactDeltaPayload(chunk=chunk))

    result = await get_llm().stream(
        model=model,
        system=load_prompt("generator"),
        user=user,
        max_tokens=MAX_GENERATOR_TOKENS,
        on_chunk=on_chunk,
    )
    ctx.add_usage(result.tokens_in, result.tokens_out, result.cost_usd)

    html = result.text.strip()
    error = (
        None
        if "<html" in html.lower()
        else f"output does not contain an <html> document (starts: {html[:160]!r})"
    )

    record_trace(
        run_id=ctx.run_id,
        session_id=ctx.session_id,
        node="generator",
        model=model,
        prompt_version=prompt_version("generator"),
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        cost_usd=result.cost_usd,
        latency_ms=int((time.monotonic() - started) * 1000),
        retry_index=retry_index,
        error=error,
    )
    if error:
        raise NodeError("generator", error)
    return html
