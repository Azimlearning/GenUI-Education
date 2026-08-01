"""Generator: the Tier 3 core. Direct-to-HTML fast model.

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

# Live probe (2026-07-18): the strong model uses an adaptive thinking block
# and can spend its entire 16k output allowance before it emits any HTML. The
# fast model produces complete direct-to-text documents reliably.  Drag labs
# include CSS, accessible pointer handling, and a real scientific readout, so
# leave ample room for the document to close cleanly instead of cutting it off
# partway through its script.
MAX_GENERATOR_TOKENS = 20_000


def extract_complete_html(raw: str) -> str | None:
    """Return exactly one complete document, dropping harmless Markdown fences.

    The model occasionally wraps an otherwise-valid reply in `````html``.
    More importantly, a ``max_tokens`` response can start with ``<html`` but
    never finish it; treating that as valid sends a broken artifact into the
    verifier and browser. Only a complete document is safe to continue with.
    """
    text = raw.strip()
    lower = text.lower()
    start = lower.find("<!doctype html")
    if start == -1:
        start = lower.find("<html")
    end = lower.rfind("</html>")
    if start == -1 or end == -1 or end < start:
        return None
    return text[start : end + len("</html>")]


async def run_generator(
    ctx: RunContext,
    plan: ArtifactPlan,
    revision_issues: list[str] | None = None,
    retry_index: int = 0,
) -> str:
    settings = get_settings()
    model = settings.model_fast
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

    html = extract_complete_html(result.text)
    if not result.text.strip():
        error = (
            "empty response "
            f"(stop_reason={result.stop_reason!r}, output_tokens={result.tokens_out}, "
            f"content_types={result.content_types!r})"
        )
    elif html is None:
        error = (
            "output does not contain a complete HTML document "
            f"(stop_reason={result.stop_reason!r}, starts: {result.text[:160]!r})"
        )
    else:
        error = None

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
    assert html is not None  # narrows the optional return after the error guard
    return html
