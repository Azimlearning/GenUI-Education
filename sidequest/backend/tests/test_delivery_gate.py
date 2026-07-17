"""The delivery gate must be structurally unbypassable (SECURITY.md section 4):
PassedVerifierReport is mintable only by the verifier module, delivery requires
it, and no other code path emits artifact_done."""

import re
from pathlib import Path

import pytest

import graph.nodes.verifier as verifier_module
from graph.context import RunContext
from graph.nodes.verifier import PassedVerifierReport
from schemas.plan import ArtifactPlan, Variable
from schemas.verifier import VerifierReport
from services.delivery import deliver_verified_artifact

BACKEND = Path(__file__).resolve().parent.parent

PLAN = ArtifactPlan(
    title="T",
    learning_objective="L",
    variables=[Variable(name="x", unit="", min=0, max=1, default=0.5)],
    governing_model="y = x",
    expected_behaviors=["y follows x"],
    layout_notes="n/a",
    library="none",
)


def test_cannot_mint_outside_verifier():
    report = VerifierReport(verdict="pass")
    with pytest.raises(TypeError):
        PassedVerifierReport(report)
    with pytest.raises(TypeError):
        PassedVerifierReport(report, _mint=object())  # forged token


def test_cannot_mint_from_fail_verdict():
    # White-box: even holding the real token, a fail verdict cannot mint.
    report = VerifierReport(verdict="fail")
    with pytest.raises(ValueError):
        PassedVerifierReport(report, _mint=verifier_module._MINT)


async def test_delivery_rejects_non_passed_types():
    async def emit(payload):
        raise AssertionError("must not emit for unverified input")

    ctx = RunContext(run_id="r", session_id="s", emit=emit)
    for fake in (VerifierReport(verdict="pass"), object(), None, "passed"):
        with pytest.raises(TypeError):
            await deliver_verified_artifact(ctx, fake, PLAN, "<html></html>")


async def test_delivery_emits_for_minted_report():
    events = []

    async def emit(payload):
        events.append(payload)

    ctx = RunContext(run_id="r", session_id="s", emit=emit)
    passed = PassedVerifierReport(VerifierReport(verdict="pass"), _mint=verifier_module._MINT)
    artifact_id = await deliver_verified_artifact(ctx, passed, PLAN, "<html></html>")
    assert artifact_id.startswith("art_")
    assert len(events) == 1 and events[0].artifact_id == artifact_id


def test_no_second_emitter_in_source():
    """artifact_done can only be constructed in the delivery service (and its
    schema definition). A second construction site anywhere in backend source
    is a review-blocking violation; this test makes it a CI failure too."""
    allowed = {
        BACKEND / "services" / "delivery.py",
        BACKEND / "schemas" / "events.py",  # class definition + registry
    }
    offenders = []
    for path in BACKEND.rglob("*.py"):
        if ".venv" in path.parts or "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"ArtifactDonePayload\s*\(", text) and path not in allowed:
            offenders.append(str(path.relative_to(BACKEND)))
    assert not offenders, f"artifact_done constructed outside the gate: {offenders}"


def test_no_second_minter_in_source():
    """PassedVerifierReport must be instantiated only inside the verifier
    module (and tests). Same structural rule as the emitter scan."""
    allowed = {BACKEND / "graph" / "nodes" / "verifier.py"}
    offenders = []
    for path in BACKEND.rglob("*.py"):
        if ".venv" in path.parts or "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"PassedVerifierReport\s*\(", text) and path not in allowed:
            offenders.append(str(path.relative_to(BACKEND)))
    assert not offenders, f"PassedVerifierReport minted outside verifier: {offenders}"
