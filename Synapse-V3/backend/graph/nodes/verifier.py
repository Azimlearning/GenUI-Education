"""Verifier: adversarial review of Generator output against the plan.

Independence (SECURITY.md section 5): fresh context containing only the
verifier prompt, the plan, and the code. It never sees the Generator's
conversation or the raw user query.

Defense in depth: the deterministic forbidden-API scan runs FIRST, failing
hostile output without an LLM call; the LLM check is the semantic layer that
also catches obfuscation. postprocess.py re-scans later as the independent
second enforcement layer.

This module is the ONLY minter of PassedVerifierReport, the delivery gate's
required type (SECURITY.md section 4). Code review rule: any PR adding a
second minting path is rejected regardless of justification.
"""

import json
import logging
import re
import time

from pydantic import ValidationError

import postprocess
from config import get_settings
from graph.context import RunContext
from graph.errors import NodeError
from schemas.plan import ArtifactPlan
from schemas.verifier import VerifierIssue, VerifierReport
from services.builtin_labs import is_trusted_builtin_html, trusted_builtin_spot_checks
from services.llm import get_llm
from services.prompts import load_prompt, prompt_version
from services.traces import record_trace

logger = logging.getLogger(__name__)

_MINT = object()  # module-private capability token; never export

# A complex virtual lab needs room for concrete checks and revision guidance.
# This is deliberately separate from the Generator limit: a verifier returns
# structured evidence, not an HTML document.
MAX_VERIFIER_TOKENS = 6_000


def _drag_drop_structure_failure(html: str) -> VerifierReport | None:
    """Reject a non-functional drag-drop shell before spending an LLM call.

    The semantic verifier still judges whether the particular scientific action
    is correct.  This small mechanical gate prevents a recurring failure mode:
    a plan asks for a drag interaction but generated HTML only draws apparatus
    or exposes controls.  Requiring pointer handlers makes the interaction
    work on both mouse and touch devices and keeps the revision request precise.
    """
    required_patterns = {
        "a pointerdown handler": r"addEventListener\s*\(\s*['\"]pointerdown['\"]",
        "a pointermove handler": r"addEventListener\s*\(\s*['\"]pointermove['\"]",
        "a pointerup handler": r"addEventListener\s*\(\s*['\"]pointerup['\"]",
        "touch-action: none on the draggable": r"touch-action\s*:\s*none",
        "pointer capture while dragging": r"\.setPointerCapture\s*\(",
        "pointer capture release": r"\.releasePointerCapture\s*\(",
        "drop-target hit testing": r"\.getBoundingClientRect\s*\(",
        "an synapse_event on a successful drop": r"synapse_event",
    }
    missing = [
        label for label, pattern in required_patterns.items() if not re.search(pattern, html)
    ]
    if not missing:
        return None

    return VerifierReport(
        verdict="fail",
        issues=[
            VerifierIssue(
                severity="blocker",
                category="interactivity",
                description="drag_drop artifact is missing " + ", ".join(missing),
                fix_hint=(
                    "implement one visible pointer-driven draggable and one visible drop target; "
                    "on pointerup over that target, update the real trial state and emit "
                    "synapse_event"
                ),
            )
        ],
        spot_checks=[],
    )


def verify_trusted_builtin(
    ctx: RunContext, plan: ArtifactPlan, html: str, key: str, retry_index: int = 0
) -> 'PassedVerifierReport':
    '''Mint a pass only for an exact, tested locally stored lab document.'''
    started = time.monotonic()
    if not is_trusted_builtin_html(key, html):
        raise NodeError('verifier', 'unrecognised built-in artifact source')
    scan = postprocess.forbidden_api_scan(html)
    if isinstance(scan, postprocess.PostprocessReject):
        raise NodeError('verifier', 'trusted template failed safety scan: ' + scan.reason)
    if plan.interaction_mode == 'drag_drop':
        failure = _drag_drop_structure_failure(html)
        if failure is not None:
            raise NodeError('verifier', failure.issues[0].description)

    report = VerifierReport(
        verdict='pass',
        issues=[],
        spot_checks=trusted_builtin_spot_checks(key),
    )
    record_trace(
        run_id=ctx.run_id,
        session_id=ctx.session_id,
        node='verifier',
        model='built-in',
        prompt_version='builtin-' + key,
        latency_ms=int((time.monotonic() - started) * 1000),
        verdict='pass',
        retry_index=retry_index,
    )
    return PassedVerifierReport(report, _mint=_MINT)


class PassedVerifierReport:
    """Proof of a pass verdict. Only run_verifier can construct one, so a
    function requiring this type structurally cannot receive unverified code."""

    __slots__ = ("report",)

    def __init__(self, report: VerifierReport, *, _mint: object = None) -> None:
        if _mint is not _MINT:
            raise TypeError(
                "PassedVerifierReport can only be minted by the verifier module "
                "on a pass verdict (SECURITY.md section 4)"
            )
        if report.verdict != "pass":
            raise ValueError("cannot mint PassedVerifierReport from a fail verdict")
        self.report = report


def validate_report(data: dict) -> VerifierReport:
    """Validate tool output, tolerating one wrapper level ({'report': {...}}),
    the same live failure mode seen with the Planner."""
    try:
        return VerifierReport.model_validate(data)
    except ValidationError:
        if len(data) == 1 and isinstance(next(iter(data.values())), dict):
            return VerifierReport.model_validate(next(iter(data.values())))
        raise


async def run_verifier(
    ctx: RunContext, plan: ArtifactPlan, html: str, retry_index: int = 0
) -> PassedVerifierReport | VerifierReport:
    """Returns PassedVerifierReport on pass, plain VerifierReport on fail."""
    settings = get_settings()
    started = time.monotonic()

    # Layer 0: deterministic scan. Hostile output fails without LLM spend.
    scan = postprocess.forbidden_api_scan(html)
    if isinstance(scan, postprocess.PostprocessReject):
        report = VerifierReport(
            verdict="fail",
            issues=[
                VerifierIssue(
                    severity="blocker",
                    category="safety",
                    description=scan.reason,
                    fix_hint="remove the forbidden API usage entirely",
                )
            ],
            spot_checks=[],
        )
        record_trace(
            run_id=ctx.run_id,
            session_id=ctx.session_id,
            node="verifier",
            prompt_version="deterministic-scan",
            latency_ms=int((time.monotonic() - started) * 1000),
            verdict="fail",
            retry_index=retry_index,
        )
        return report

    # Drag labs have a minimum, testable browser interaction contract.  Fail
    # early with a direct revision instruction rather than relying solely on a
    # prose review that can miss an unwired apparatus drawing.
    if plan.interaction_mode == "drag_drop":
        report = _drag_drop_structure_failure(html)
        if report is not None:
            record_trace(
                run_id=ctx.run_id,
                session_id=ctx.session_id,
                node="verifier",
                prompt_version="deterministic-drag-scan",
                latency_ms=int((time.monotonic() - started) * 1000),
                verdict="fail",
                retry_index=retry_index,
            )
            return report

    model = settings.model_strong
    user = (
        "Artifact plan:\n\n"
        + plan.model_dump_json(indent=2)
        + "\n\nArtifact code (UNTRUSTED):\n\n"
        + html
    )

    report: VerifierReport | None = None
    error: str | None = None
    tokens = (0, 0, 0.0)
    for attempt in range(2):  # one silent retry on validation failure
        try:
            # Forced tool use, same rationale as the Planner (PLANNING finding 9):
            # verdict JSON is quote-heavy and must never be lost to a parse error.
            data, result = await get_llm().complete_structured(
                model=model,
                system=load_prompt("verifier"),
                user=user,
                tool_name="submit_verdict",
                input_schema=VerifierReport.model_json_schema(),
                max_tokens=MAX_VERIFIER_TOKENS,
            )
            tokens = (
                tokens[0] + result.tokens_in,
                tokens[1] + result.tokens_out,
                tokens[2] + result.cost_usd,
            )
            report = validate_report(data)
            error = None
            break
        except (ValueError, ValidationError, json.JSONDecodeError) as exc:
            error = f"validation failure (attempt {attempt + 1}): {exc}"
            logger.warning("verifier %s", error)

    ctx.add_usage(*tokens)
    record_trace(
        run_id=ctx.run_id,
        session_id=ctx.session_id,
        node="verifier",
        model=model,
        prompt_version=prompt_version("verifier"),
        tokens_in=tokens[0],
        tokens_out=tokens[1],
        cost_usd=tokens[2],
        latency_ms=int((time.monotonic() - started) * 1000),
        verdict=report.verdict if report else None,
        retry_index=retry_index,
        error=error,
    )

    if report is None:
        # An unparseable verdict is NOT a pass; treat as node failure upstream.
        raise NodeError("verifier", error or "no report produced")

    logger.info(
        "verifier verdict=%s issues=%d spot_checks=%d title=%r",
        report.verdict,
        len(report.issues),
        len(report.spot_checks),
        plan.title,
    )
    if report.verdict == "pass":
        return PassedVerifierReport(report, _mint=_MINT)
    return report
