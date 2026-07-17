"""The delivery gate: the only path to an artifact_done event.

`deliver_verified_artifact` requires a PassedVerifierReport, a type only the
verifier module can mint, and only on a pass verdict. There is no other
constructor and no other emitter of ArtifactDonePayload in the codebase
(enforced by tests/test_delivery_gate.py's source scan). Bypassing
verification is therefore a type error, not a code-review catch
(SECURITY.md section 4).
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
    """Emit artifact_done for a verified, post-processed artifact."""
    if not isinstance(passed, PassedVerifierReport):  # runtime belt-and-braces
        raise TypeError("delivery requires a PassedVerifierReport from the verifier")
    artifact_id = f"art_{uuid.uuid4().hex[:8]}"
    await ctx.emit(ArtifactDonePayload(artifact_id=artifact_id, title=plan.title, html=html))
    return artifact_id
