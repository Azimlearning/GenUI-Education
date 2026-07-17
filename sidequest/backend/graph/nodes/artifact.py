"""The artifact branch: Planner -> [Generator -> Verifier]xN -> Post-processor
-> delivery gate.

Phase 2 shape: verifier fail routes back to the Generator with the issues list
as a revision request, max 2 retries, then the graceful-degradation path. A
post-process reject counts as a verifier fail for retry purposes (SECURITY.md
section 3). Delivery happens exclusively through
services.delivery.deliver_verified_artifact, which requires the
PassedVerifierReport type only the verifier can mint.

Runs under the artifact timeout in parallel with the Explainer (Phase 3); the
text branch is never blocked by anything here. Every failure degrades to
artifact_failed with honest copy (principle 4).
"""

import asyncio
import logging
import time

from langchain_core.runnables import RunnableConfig

import postprocess
from config import get_settings
from graph.context import RunContext, get_ctx
from graph.errors import NodeError
from graph.nodes.generator import run_generator
from graph.nodes.planner import run_planner
from graph.nodes.verifier import PassedVerifierReport, run_verifier
from graph.state import PipelineState
from schemas.events import ArtifactFailedPayload, ArtifactStatusPayload
from services.delivery import deliver_verified_artifact
from services.traces import record_trace

logger = logging.getLogger(__name__)

MAX_GENERATOR_RETRIES = 2  # revisions after the first attempt (guardrail)

# A revision cycle (generation + verification) needs this much runway; if less
# remains before the branch timeout, degrade honestly instead of starting a
# doomed attempt that burns tokens and gets killed mid-flight.
MIN_RETRY_HEADROOM_S = 90

DEGRADE_COPY = "I couldn't build a stable interactive piece for this one."


def _check_budget(ctx: RunContext) -> None:
    if ctx.usage.cost_usd >= get_settings().max_run_cost_usd:
        raise NodeError("budget", "per-run cost ceiling reached")


def _revision_issues(report) -> list[str]:
    issues = [
        f"[{issue.category}/{issue.severity}] {issue.description} Fix: {issue.fix_hint}"
        for issue in report.issues
        if issue.severity in ("blocker", "major")
    ]
    return issues or ["The verifier failed the artifact; produce a corrected version."]


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
    failure_reason = "verification_failed"
    try:
        async with asyncio.timeout(settings.artifact_timeout_s):
            await ctx.emit(ArtifactStatusPayload(stage="planning"))
            plan = await run_planner(ctx, state["query"], intent.artifact_type, intent.domain)

            deadline = started + settings.artifact_timeout_s
            issues: list[str] | None = None
            last_report_dump: dict | None = None
            for attempt in range(MAX_GENERATOR_RETRIES + 1):
                _check_budget(ctx)
                if attempt > 0 and deadline - time.monotonic() < MIN_RETRY_HEADROOM_S:
                    logger.warning(
                        "skipping revision %d: only %.0fs left before branch timeout",
                        attempt,
                        deadline - time.monotonic(),
                    )
                    break
                await ctx.emit(
                    ArtifactStatusPayload(stage="generating" if attempt == 0 else "revising")
                )
                try:
                    html = await run_generator(
                        ctx, plan, revision_issues=issues, retry_index=attempt
                    )
                except NodeError as exc:
                    # Invalid generator output counts as a verifier fail for
                    # retry purposes (SYSTEM_ARCHITECTURE.md failure taxonomy).
                    logger.warning("generator invalid output (attempt %d): %s", attempt + 1, exc)
                    issues = [
                        "[safety/blocker] Your previous reply was not a complete HTML "
                        "document. Output ONLY the full document, <!doctype html> "
                        "through </html>, with no commentary."
                    ]
                    continue

                await ctx.emit(ArtifactStatusPayload(stage="verifying"))
                outcome = await run_verifier(ctx, plan, html, retry_index=attempt)

                if not isinstance(outcome, PassedVerifierReport):
                    last_report_dump = outcome.model_dump()
                    issues = _revision_issues(outcome)
                    logger.info(
                        "verifier fail (attempt %d/%d): %d issue(s)",
                        attempt + 1,
                        MAX_GENERATOR_RETRIES + 1,
                        len(outcome.issues),
                    )
                    continue

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
                    retry_index=attempt,
                    error=(
                        f"{processed.rule}: {processed.reason}"
                        if isinstance(processed, postprocess.PostprocessReject)
                        else None
                    ),
                )
                if isinstance(processed, postprocess.PostprocessReject):
                    # Counts as a verifier fail for retry purposes; never auto-strip.
                    logger.warning(
                        "postprocess reject (attempt %d): %s: %s",
                        attempt + 1,
                        processed.rule,
                        processed.reason,
                    )
                    last_report_dump = outcome.report.model_dump()
                    issues = [
                        f"[safety/blocker] Post-processor rejected the document: "
                        f"{processed.reason}. Fix: remove it entirely."
                    ]
                    continue

                artifact_id = await deliver_verified_artifact(ctx, outcome, plan, processed)
                ctx.artifact_total_ms = int((time.monotonic() - started) * 1000)
                return {
                    "artifact_plan": plan.model_dump(),
                    "artifact_code": processed,
                    "verification_report": outcome.report.model_dump(),
                    "retry_count": attempt,
                    "final_artifact_id": artifact_id,
                }

            # Retries exhausted.
            await ctx.emit(
                ArtifactFailedPayload(
                    reason="verification_failed",
                    detail_user=DEGRADE_COPY
                    + " It didn't pass the science check after several tries.",
                    retryable=True,
                )
            )
            return {
                "failure_reason": failure_reason,
                "verification_report": last_report_dump,
                "retry_count": MAX_GENERATOR_RETRIES,
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
