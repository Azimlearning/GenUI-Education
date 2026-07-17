"""Verifier: Phase 1 log-only stub.

Runs the deterministic forbidden-API scan and records a report shaped exactly
like the Phase 2 LLM verifier's, but NEVER blocks delivery (PLANNING.md Phase 1:
"logs a report, never blocks"). The post-processor's own scan remains the
enforcing safety layer this phase; the real adversarial LLM verifier and the
PassedVerifierReport delivery gate land in Phase 2.
"""

import logging
import time

import postprocess
from graph.context import RunContext
from schemas.plan import ArtifactPlan
from schemas.verifier import VerifierIssue, VerifierReport
from services.traces import record_trace

logger = logging.getLogger(__name__)


async def run_verifier_stub(ctx: RunContext, plan: ArtifactPlan, html: str) -> VerifierReport:
    started = time.monotonic()

    issues: list[VerifierIssue] = []
    scan = postprocess.forbidden_api_scan(html)
    if isinstance(scan, postprocess.PostprocessReject):
        issues.append(
            VerifierIssue(
                severity="blocker",
                category="safety",
                description=scan.reason,
                fix_hint="remove the forbidden API usage entirely",
            )
        )

    report = VerifierReport(
        verdict="fail" if issues else "pass",
        issues=issues,
        spot_checks=[],
        mode="stub_log_only",
    )
    logger.info(
        "verifier(stub) verdict=%s issues=%d title=%r",
        report.verdict,
        len(report.issues),
        plan.title,
    )
    record_trace(
        run_id=ctx.run_id,
        session_id=ctx.session_id,
        node="verifier",
        model=None,
        prompt_version="verifier-stub",
        latency_ms=int((time.monotonic() - started) * 1000),
        verdict=report.verdict,
    )
    return report
