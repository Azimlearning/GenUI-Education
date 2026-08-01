"""Verifier node tests: layer-0 deterministic scan (no LLM spend on hostile
output), structured-output validation, and minting semantics."""

import pytest

import config
import graph.nodes.verifier as verifier_module
from graph.context import RunContext
from graph.errors import NodeError
from graph.nodes.verifier import PassedVerifierReport, run_verifier
from schemas.plan import ArtifactPlan, Variable

PLAN = ArtifactPlan(
    title="T",
    learning_objective="L",
    variables=[Variable(name="x", unit="", min=0, max=1, default=0.5)],
    governing_model="y = x",
    expected_behaviors=["y follows x"],
    layout_notes="n/a",
    library="none",
    study_note="y follows x directly.",
)

DRAG_PLAN = ArtifactPlan(
    title="Drop Lab",
    learning_objective="See a state change after one meaningful drop.",
    variables=[Variable(name="drops", unit="", min=0, max=5, default=0)],
    governing_model="each drop increases the measured amount by one unit",
    expected_behaviors=["a successful drop increases the readout"],
    layout_notes="Drag the sample into the visible vessel, then read the result.",
    library="none",
    interaction_mode="drag_drop",
    study_note="One successful drop changes the measured state.",
    steps=["Drag the sample onto the vessel.", "Read the updated result."],
)

PASS_DATA = {
    "verdict": "pass",
    "issues": [],
    "spot_checks": [
        {"inputs": "x=0.5", "expected": "0.5", "code_derived": "0.5"},
        {"inputs": "x=0", "expected": "0", "code_derived": "0"},
        {"inputs": "x=1", "expected": "1", "code_derived": "1"},
    ],
}

FAIL_DATA = {
    "verdict": "fail",
    "issues": [
        {
            "severity": "blocker",
            "category": "science",
            "description": "wrong constant",
            "fix_hint": "use 9.81",
        }
    ],
    "spot_checks": [],
}

CLEAN_HTML = (
    "<!doctype html><html><head></head><body>"
    "<script>window.parent.postMessage({type:'synapse_ready'},'*');</script></body></html>"
)
HOSTILE_HTML = CLEAN_HTML.replace("<body>", "<body><script>fetch('/x')</script>")
DRAG_HTML = (
    "<!doctype html><html><head><style>#sample { touch-action: none; }</style></head>"
    "<body><div id='stage'><button id='sample'>sample</button>"
    "<div id='target'>vessel</div></div>"
    "<script>const sample=document.getElementById('sample');"
    "const stage=document.getElementById('stage');"
    "const target=document.getElementById('target');let dragging=false;"
    "sample.addEventListener('pointerdown',e=>{dragging=true;"
    "sample.setPointerCapture(e.pointerId);});"
    "sample.addEventListener('pointermove',e=>{if(!dragging)return;"
    "const r=stage.getBoundingClientRect();"
    "sample.style.left=(e.clientX-r.left)+'px';});"
    "sample.addEventListener('pointerup',e=>{dragging=false;"
    "sample.releasePointerCapture(e.pointerId);"
    "const r=target.getBoundingClientRect();"
    "window.parent.postMessage({type:'synapse_event'},'*');});"
    "</script></body></html>"
)


@pytest.fixture(autouse=True)
def live_mode(monkeypatch):
    monkeypatch.setenv("ECHO_MODE", "false")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    config.get_settings.cache_clear()
    monkeypatch.setattr(verifier_module, "record_trace", lambda **kw: None)
    yield
    config.get_settings.cache_clear()


class FakeLLM:
    """Stands in for LLMClient.complete_structured."""

    def __init__(self, data: dict):
        self.data = data
        self.calls = 0

    async def complete_structured(self, **kwargs):
        self.calls += 1

        class R:
            tokens_in = 100
            tokens_out = 50
            cost_usd = 0.001

        return self.data, R()


def make_ctx() -> RunContext:
    async def emit(payload):
        pass

    return RunContext(run_id="r", session_id="s", emit=emit)


async def test_hostile_output_fails_without_llm_call(monkeypatch):
    llm = FakeLLM(PASS_DATA)
    monkeypatch.setattr(verifier_module, "get_llm", lambda: llm)
    outcome = await run_verifier(make_ctx(), PLAN, HOSTILE_HTML)
    assert not isinstance(outcome, PassedVerifierReport)
    assert outcome.verdict == "fail"
    assert outcome.issues[0].category == "safety"
    assert llm.calls == 0  # layer-0 scan caught it; zero LLM spend


async def test_drag_drop_requires_real_pointer_workflow_without_llm_call(monkeypatch):
    llm = FakeLLM(PASS_DATA)
    monkeypatch.setattr(verifier_module, "get_llm", lambda: llm)
    outcome = await run_verifier(make_ctx(), DRAG_PLAN, CLEAN_HTML)
    assert not isinstance(outcome, PassedVerifierReport)
    assert outcome.verdict == "fail"
    assert outcome.issues[0].category == "interactivity"
    assert "pointerdown handler" in outcome.issues[0].description
    assert llm.calls == 0


async def test_drag_drop_pointer_workflow_reaches_semantic_verifier(monkeypatch):
    llm = FakeLLM(PASS_DATA)
    monkeypatch.setattr(verifier_module, "get_llm", lambda: llm)
    outcome = await run_verifier(make_ctx(), DRAG_PLAN, DRAG_HTML)
    assert isinstance(outcome, PassedVerifierReport)
    assert llm.calls == 1


async def test_pass_verdict_mints_passed_report(monkeypatch):
    monkeypatch.setattr(verifier_module, "get_llm", lambda: FakeLLM(PASS_DATA))
    outcome = await run_verifier(make_ctx(), PLAN, CLEAN_HTML)
    assert isinstance(outcome, PassedVerifierReport)
    assert outcome.report.verdict == "pass"
    assert len(outcome.report.spot_checks) == 3


async def test_fail_verdict_returns_plain_report(monkeypatch):
    monkeypatch.setattr(verifier_module, "get_llm", lambda: FakeLLM(FAIL_DATA))
    outcome = await run_verifier(make_ctx(), PLAN, CLEAN_HTML)
    assert not isinstance(outcome, PassedVerifierReport)
    assert outcome.verdict == "fail"


async def test_long_spot_check_is_a_valid_verdict(monkeypatch):
    # Multi-step science traces are useful evidence, not malformed output.
    data = {
        "verdict": "pass",
        "issues": [],
        "spot_checks": [
            {"inputs": "x=0.5", "expected": "0.5", "code_derived": "0.5"},
            {
                "inputs": "temperature=70 C",
                "expected": "rate falls after denaturation",
                "code_derived": "k=... " * 200,
            },
            {"inputs": "x=1", "expected": "1", "code_derived": "1"},
        ],
    }
    monkeypatch.setattr(verifier_module, "get_llm", lambda: FakeLLM(data))
    outcome = await run_verifier(make_ctx(), PLAN, CLEAN_HTML)
    assert isinstance(outcome, PassedVerifierReport)
    assert len(outcome.report.spot_checks[1].code_derived) > 600


async def test_overlong_spot_check_is_bounded_without_losing_the_verdict(monkeypatch):
    data = {
        "verdict": "pass",
        "issues": [],
        "spot_checks": [
            {"inputs": "x=0.5", "expected": "0.5", "code_derived": "0.5"},
            {
                "inputs": "temperature=70 C",
                "expected": "rate falls after denaturation",
                "code_derived": "k=... " * 1_500,
            },
            {"inputs": "x=1", "expected": "1", "code_derived": "1"},
        ],
    }
    monkeypatch.setattr(verifier_module, "get_llm", lambda: FakeLLM(data))
    outcome = await run_verifier(make_ctx(), PLAN, CLEAN_HTML)
    assert isinstance(outcome, PassedVerifierReport)
    code_derived = outcome.report.spot_checks[1].code_derived
    assert len(code_derived) == 8_000
    assert code_derived.endswith(" [truncated]")


async def test_schema_violating_verdict_is_not_a_pass(monkeypatch):
    # Even with forced tool use, the model could emit enum-violating values;
    # that must surface as a typed node failure, never a silent pass.
    llm = FakeLLM({"verdict": "looks_great", "issues": [], "spot_checks": []})
    monkeypatch.setattr(verifier_module, "get_llm", lambda: llm)
    with pytest.raises(NodeError):
        await run_verifier(make_ctx(), PLAN, CLEAN_HTML)
    assert llm.calls == 2  # one silent retry, then typed failure
