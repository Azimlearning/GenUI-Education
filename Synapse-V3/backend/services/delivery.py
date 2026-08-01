"""The delivery gate: the only module that emits an artifact_done event.

Two paths, one security boundary:

`deliver_verified_artifact` requires a PassedVerifierReport, a type only the
verifier module can mint, and only on a pass verdict. It emits verified=True.
This is the trust path: a "science checked" badge is only ever shown for an
artifact that went through here.

`deliver_unverified_artifact` exists for the science/pedagogy-failure case: an
otherwise usable artifact the Verifier rejected after its retries. It emits
verified=False so the client shows an honest "not fully verified" note and NO
reward. It is deliberately NOT gated on a
PassedVerifierReport, so the caller (graph/nodes/artifact.py) is responsible for
the delivery boundary: it is only reached when the failure carried no safety,
behavior, or interactivity issue AND the html has passed postprocess safety-
hardening (forbidden-API rescan, CSP, size cap). An artifact that fails on any
of those grounds never reaches this path.

Both emitters live in this module on purpose: tests/test_delivery_gate.py's
source scan forbids constructing ArtifactDonePayload anywhere else, so the set
of delivery paths stays auditable in one file (SECURITY.md section 4).
"""

import uuid

from graph.context import RunContext
from graph.nodes.verifier import PassedVerifierReport
from schemas.events import ArtifactDonePayload
from schemas.plan import ArtifactPlan


async def deliver_verified_artifact(
    ctx: RunContext,
    passed: PassedVerifierReport,
    plan: ArtifactPlan,
    html: str,
) -> str:
    """Emit artifact_done for a verified, post-processed artifact (verified=True)."""
    if not isinstance(passed, PassedVerifierReport):  # runtime belt-and-braces
        raise TypeError("delivery requires a PassedVerifierReport from the verifier")
    artifact_id = f"art_{uuid.uuid4().hex[:8]}"
    await ctx.emit(
        ArtifactDonePayload(artifact_id=artifact_id, title=plan.title, html=html, verified=True)
    )
    return artifact_id


async def deliver_unverified_artifact(
    ctx: RunContext,
    plan: ArtifactPlan,
    html: str,
) -> str:
    """Emit artifact_done (verified=False) for a safe-but-inaccurate artifact.

    Not gated on a PassedVerifierReport by design; the caller guarantees this is
    only reached for a science/pedagogy-only failure whose html cleared
    postprocess. See the module docstring for the delivery contract. Never emits
    a "science checked" signal: the payload's verified=False drives the client's
    honest note.
    """
    artifact_id = f"art_{uuid.uuid4().hex[:8]}"
    await ctx.emit(
        ArtifactDonePayload(artifact_id=artifact_id, title=plan.title, html=html, verified=False)
    )
    return artifact_id
