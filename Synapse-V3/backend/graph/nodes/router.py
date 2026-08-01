"""Router node: classify the query into an Intent and emit the `meta` event.

Fast model, strict JSON, one silent retry on parse failure. If both attempts
fail we fall back to text_only so the Explainer still runs; the failure is
recorded in the trace. The text branch must never be blocked (principle 3).
"""

import asyncio
import json
import logging
import re
import time

from langchain_core.runnables import RunnableConfig
from pydantic import ValidationError

from config import get_settings
from graph.context import get_ctx
from graph.state import PipelineState
from schemas.events import MetaPayload
from schemas.intent import Intent
from services.builtin_labs import is_koh_titration_brief, is_yeast_fermentation_products_brief
from services.llm import get_llm
from services.local_router import get_local_router, shadow_details
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

# A mechanism's products, stages, or inputs/outputs are learnable through an
# interactive diagram even when the user phrases the question as a lookup.
# Keep this deliberately scoped to chemistry and biology so atomic facts such
# as a boiling point remain text-only.
_PROCESS_LOOKUP_RE = re.compile(
    r"\b(products?|reactants?|inputs?|outputs?|stages?|steps?|pathway|cycle|mechanism|"
    r"fermentation|respiration|photosynthesis|transcription|translation|digestion|metabolism)\b",
    re.IGNORECASE,
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
    data = json.loads(text[start : end + 1])
    # canonical_concept must be lowercase snake_case (schemas/intent.py), but
    # the model reaches for standard scientific notation like "pH" even when
    # told to use snake_case, which fails validation and can silently
    # misroute a legitimate query to the text_only fallback. Lowercasing is
    # deterministic, preserves cache-key stability, and never changes a
    # value that was already valid.
    if isinstance(data.get("canonical_concept"), str):
        data["canonical_concept"] = data["canonical_concept"].lower()
    return Intent.model_validate(data)


def promote_process_lookup(query: str, intent: Intent) -> Intent:
    """Route science mechanisms to an explorable artifact, not a fact card."""
    if (
        intent.artifact_type == "text_only"
        and intent.domain in {"chemistry", "biology"}
        and _PROCESS_LOOKUP_RE.search(query)
    ):
        return intent.model_copy(
            update={"artifact_type": "explorable_diagram", "complexity": max(2, intent.complexity)}
        )
    return intent


def promote_builtin_lab(query: str, intent: Intent) -> Intent:
    '''Route supported deterministic lab briefs without LLM ambiguity.'''
    if is_koh_titration_brief(query):
        return Intent(
            artifact_type='virtual_experiment',
            domain='chemistry',
            complexity=3,
            canonical_concept='koh_titration_unknown_concentration',
        )
    if is_yeast_fermentation_products_brief(query):
        return Intent(
            artifact_type='virtual_experiment',
            domain='biology',
            complexity=3,
            canonical_concept='yeast_fermentation_products',
        )
    return intent


async def router_node(state: PipelineState, config: RunnableConfig) -> PipelineState:
    ctx = get_ctx(config)
    settings = get_settings()
    started = time.monotonic()

    intent: Intent
    error: str | None = None
    model: str | None = None
    tokens = (0, 0, 0.0)

    # Begin student inference alongside the LLM so its warm work is normally
    # hidden under the authoritative router call. It is observation only.
    shadow_task: asyncio.Task | None = None
    if settings.router_mode == "shadow" and settings.llm_enabled:
        shadow_task = asyncio.create_task(get_local_router().classify(state["query"]))

    if not settings.llm_enabled:
        logger.warning("ECHO MODE: no ANTHROPIC_API_KEY; router returning static intent")
        intent = promote_builtin_lab(state["query"], ECHO_INTENT)
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
                intent = promote_builtin_lab(
                    state["query"],
                    promote_process_lookup(state["query"], parse_intent(result.text)),
                )
                error = None
                break
            except (ValueError, ValidationError, json.JSONDecodeError) as exc:
                error = f"parse failure (attempt {attempt + 1}): {exc}"
                logger.warning("router %s", error)

    # A supported deterministic lab still wins when both model JSON responses
    # were malformed and the ordinary route would otherwise remain text-only.
    intent = promote_builtin_lab(state['query'], intent)

    ctx.add_usage(*tokens)

    if shadow_task is not None:
        try:
            local = await shadow_task
            details = shadow_details(intent, local)
            shadow_error = None
        except Exception as exc:
            # Optional TensorFlow/model failures must never change LLM routing.
            details = None
            shadow_error = str(exc)
            logger.warning("router shadow unavailable: %s", shadow_error)
        record_trace(
            run_id=ctx.run_id,
            session_id=ctx.session_id,
            node="router_shadow",
            model="router_student.keras",
            latency_ms=local.latency_ms if shadow_error is None else None,
            verdict="agree" if details and details["agreement"]["all"] else "disagree",
            error=shadow_error,
            details=details,
        )

    # Emit meta first: the client is waiting on it, and the trace write is
    # background telemetry (Phase 0 has no cache node; every request is a miss).
    await ctx.emit(
        MetaPayload(intent=intent.public, canonical_concept=intent.canonical_concept, cache="miss")
    )
    record_trace(
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
    return {"intent": intent, "canonical_concept": intent.canonical_concept}
