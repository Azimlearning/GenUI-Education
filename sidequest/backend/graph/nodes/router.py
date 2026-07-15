"""Router node: classify the query into an Intent and emit the `meta` event.

Fast model, strict JSON, one silent retry on parse failure. If both attempts
fail we fall back to text_only so the Explainer still runs; the failure is
recorded in the trace. The text branch must never be blocked (principle 3).
"""

import json
import logging
import time

from langchain_core.runnables import RunnableConfig
from pydantic import ValidationError

from config import get_settings
from graph.context import get_ctx
from graph.state import PipelineState
from schemas.events import MetaPayload
from schemas.intent import Intent
from services.llm import get_llm
from services.prompts import load_prompt, prompt_version
from services.traces import record_trace

logger = logging.getLogger(__name__)

FALLBACK_INTENT = Intent(
    artifact_type="text_only",
    domain="math_adjacent",
    complexity=1,
    canonical_concept="unclassified_query",
)

ECHO_INTENT = Intent(
    artifact_type="text_only",
    domain="math_adjacent",
    complexity=1,
    canonical_concept="echo_mode",
)


def parse_intent(raw: str) -> Intent:
    """Parse a strict-JSON intent, tolerating stray fences or surrounding prose."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in router output")
    return Intent.model_validate(json.loads(text[start : end + 1]))


async def router_node(state: PipelineState, config: RunnableConfig) -> PipelineState:
    ctx = get_ctx(config)
    settings = get_settings()
    started = time.monotonic()

    intent: Intent
    error: str | None = None
    model: str | None = None
    tokens = (0, 0, 0.0)

    if not settings.llm_enabled:
        logger.warning("ECHO MODE: no ANTHROPIC_API_KEY; router returning static intent")
        intent = ECHO_INTENT
    else:
        model = settings.model_fast
        llm = get_llm()
        system = load_prompt("router")
        intent = FALLBACK_INTENT
        for attempt in range(2):  # one silent retry on parse failure
            result = await llm.complete(
                model=model, system=system, user=state["query"], max_tokens=256
            )
            tokens = (
                tokens[0] + result.tokens_in,
                tokens[1] + result.tokens_out,
                tokens[2] + result.cost_usd,
            )
            try:
                intent = parse_intent(result.text)
                error = None
                break
            except (ValueError, ValidationError, json.JSONDecodeError) as exc:
                error = f"parse failure (attempt {attempt + 1}): {exc}"
                logger.warning("router %s", error)

    ctx.add_usage(*tokens)
    await record_trace(
        run_id=ctx.run_id,
        session_id=ctx.session_id,
        node="router",
        model=model,
        prompt_version=prompt_version("router") if model else None,
        tokens_in=tokens[0],
        tokens_out=tokens[1],
        cost_usd=tokens[2],
        latency_ms=int((time.monotonic() - started) * 1000),
        error=error,
    )

    # Phase 0 has no cache node yet; every request is a miss by definition.
    await ctx.emit(
        MetaPayload(intent=intent.public, canonical_concept=intent.canonical_concept, cache="miss")
    )
    return {"intent": intent, "canonical_concept": intent.canonical_concept}
