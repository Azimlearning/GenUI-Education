"""The artifact branch: Planner -> Generator -> Verifier(stub) -> Post-processor.

Phase 1 shape: one pass, no revision loop (the verifier retry loop is Phase 2).
Runs under the 30s artifact timeout; every failure degrades to artifact_failed
with honest copy and never breaks the already-streamed text (principle 4).
Phase 3 moves this branch parallel to the Explainer.
"""

import asyncio
import logging
import time
import uuid

from langchain_core.runnables import RunnableConfig

import postprocess
from config import get_settings
from graph.context import RunContext, get_ctx
from graph.errors import NodeError
from graph.nodes.generator import run_generator
from graph.nodes.planner import run_planner
from graph.nodes.verifier import run_verifier_stub
from graph.state import PipelineState
from schemas.events import ArtifactDonePayload, ArtifactFailedPayload, ArtifactStatusPayload
from services.traces import record_trace

logger = logging.getLogger(__name__)

DEGRADE_COPY = "I couldn't build a stable interactive piece for this one."


def _budget_left(ctx: RunContext) -> bool:
    return ctx.usage.cost_usd < get_settings().max_run_cost_usd


async def artifact_branch(state: PipelineState, config: RunnableConfig) -> PipelineState:
    ctx = get_ctx(config)
    settings = get_settings()
    intent = state.get("intent")

    if intent is None or intent.artifact_type == "text_only" or settings.artifacts_disabled:
        return {}
    if not settings.llm_enabled:
        logger.warning("ECHO MODE: skipping artifact branch")
        return {}

    started = time.monotonic()
    try:
        async with asyncio.timeout(settings.artifact_timeout_s):
            await ctx.emit(ArtifactStatusPayload(stage="planning"))
            plan = await run_planner(
                ctx, state["query"], intent.artifact_type, intent.domain
            )

            if not _budget_left(ctx):
                raise NodeError("budget", "per-run cost ceiling reached before generation")

            await ctx.emit(ArtifactStatusPayload(stage="generating"))
            html = await run_generator(ctx, plan)

            await ctx.emit(ArtifactStatusPayload(stage="verifying"))
            await run_verifier_stub(ctx, plan, html)  # log-only in Phase 1

            await ctx.emit(ArtifactStatusPayload(stage="postprocessing"))
            processed = postprocess.run(
                html,
                public_origin=settings.public_origin,
                max_bytes=settings.max_artifact_bytes,
            )
            record_trace(
                run_id=ctx.run_id,
                session_id=ctx.session_id,
                node="postprocess",
                latency_ms=0,
                error=(
                    f"{processed.rule}: {processed.reason}"
                    if isinstance(processed, postprocess.PostprocessReject)
                    else None
                ),
            )
            if isinstance(processed, postprocess.PostprocessReject):
                logger.warning("postprocess reject: %s: %s", processed.rule, processed.reason)
                await ctx.emit(
                    ArtifactFailedPayload(
                        reason=f"postprocess_reject:{processed.rule}",
                        detail_user=DEGRADE_COPY,
                        retryable=True,
                    )
                )
                return {"failure_reason": processed.reason}

            artifact_id = f"art_{uuid.uuid4().hex[:8]}"
            ctx.artifact_total_ms = int((time.monotonic() - started) * 1000)
            await ctx.emit(
                ArtifactDonePayload(artifact_id=artifact_id, title=plan.title, html=processed)
            )
            return {
                "artifact_plan": plan.model_dump(),
                "artifact_code": processed,
                "final_artifact_id": artifact_id,
            }

    except TimeoutError:
        logger.warning("artifact branch timed out after %ss", settings.artifact_timeout_s)
        await ctx.emit(
            ArtifactFailedPayload(
                reason="timeout",
                detail_user=DEGRADE_COPY + " It took too long to build.",
                retryable=True,
            )
        )
        return {"failure_reason": "timeout"}
    except NodeError as exc:
        logger.warning("artifact branch failed: %s", exc)
        await ctx.emit(
            ArtifactFailedPayload(
                reason=f"{exc.node}_failed",
                detail_user=DEGRADE_COPY,
                retryable=exc.node != "budget",
            )
        )
        return {"failure_reason": str(exc)}
    except Exception:
        logger.exception("artifact branch crashed")
        await ctx.emit(
            ArtifactFailedPayload(
                reason="internal_error", detail_user=DEGRADE_COPY, retryable=True
            )
        )
        return {"failure_reason": "internal_error"}
