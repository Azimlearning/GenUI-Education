"""Artifact branch integration tests with mocked LLM nodes: retry loop,
degradation, and the delivery gate in the loop (EVALS.md: mocked fixtures keep
CI deterministic and free)."""

import pytest
from pydantic import BaseModel

import config
import graph.nodes.artifact as artifact_module
import graph.nodes.verifier as verifier_module
from graph.context import RunContext
from graph.errors import NodeError
from graph.nodes.artifact import artifact_branch
from graph.nodes.verifier import PassedVerifierReport
from schemas.events import ArtifactDonePayload, ArtifactFailedPayload, ArtifactStatusPayload
from schemas.intent import Intent
from schemas.plan import ArtifactPlan, Variable
from schemas.verifier import VerifierIssue, VerifierReport

PLAN = ArtifactPlan(
    title="Projectile Motion Lab",
    learning_objective="See how angle sets range.",
    variables=[Variable(name="angle", unit="deg", min=15, max=75, default=45)],
    governing_model="y(t) = v0*sin(theta)*t - 0.5*9.81*t^2",
    expected_behaviors=["range peaks at 45 degrees"],
    layout_notes="canvas top, controls below",
    library="p5",
)

GOOD_HTML = (
    "<!doctype html><html><head><title>t</title></head><body>"
    "<script src=\"/vendor/p5.min.js\"></script>"
    "<script>window.parent.postMessage({type:'axiom_ready'},'*');</script>"
    "</body></html>"
)

HOSTILE_HTML = GOOD_HTML.replace(
    "<body>", "<body><script>fetch('https://example.com/log')</script>"
)

SIM_INTENT = Intent(
    artifact_type="simulation", domain="physics", complexity=2,
    canonical_concept="projectile_motion",
)
TEXT_INTENT = Intent(
    artifact_type="text_only", domain="physics", complexity=1,
    canonical_concept="boiling_point_gold",
)


def passed() -> PassedVerifierReport:
    return PassedVerifierReport(
        VerifierReport(verdict="pass"), _mint=verifier_module._MINT
    )


def failed(description: str = "wrong sign on g") -> VerifierReport:
    return VerifierReport(
        verdict="fail",
        issues=[
            VerifierIssue(
                severity="blocker",
                category="science",
                description=description,
                fix_hint="negate the gravity term",
            )
        ],
    )


@pytest.fixture(autouse=True)
def live_mode(monkeypatch):
    """The branch requires llm_enabled; LLM calls themselves are patched out."""
    monkeypatch.setenv("ECHO_MODE", "false")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


def _sync_noop(*args, **kwargs):
    return None


async def run_branch(monkeypatch, intent, htmls, verdicts):
    """htmls: generator outputs per attempt; verdicts: verifier outcomes per
    attempt (PassedVerifierReport | VerifierReport | Exception)."""
    events: list[BaseModel] = []
    generator_calls: list[list[str] | None] = []

    async def emit(payload):
        events.append(payload)

    async def fake_planner(ctx, query, artifact_type, domain):
        return PLAN

    async def fake_generator(ctx, plan, revision_issues=None, retry_index=0):
        generator_calls.append(revision_issues)
        return htmls[min(retry_index, len(htmls) - 1)]

    async def fake_verifier(ctx, plan, html, retry_index=0):
        outcome = verdicts[min(retry_index, len(verdicts) - 1)]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(artifact_module, "run_planner", fake_planner)
    monkeypatch.setattr(artifact_module, "run_generator", fake_generator)
    monkeypatch.setattr(artifact_module, "run_verifier", fake_verifier)
    monkeypatch.setattr(artifact_module, "record_trace", _sync_noop)

    ctx = RunContext(run_id="run_test", session_id="sess_test", emit=emit)
    state = {"query": "show me projectile motion", "intent": intent, "retry_count": 0}
    result = await artifact_branch(state, {"configurable": {"ctx": ctx}})
    return events, result, generator_calls


def stages(events):
    return [e.stage for e in events if isinstance(e, ArtifactStatusPayload)]


async def test_text_only_intent_skips_branch(monkeypatch):
    events, result, _ = await run_branch(monkeypatch, TEXT_INTENT, [GOOD_HTML], [passed()])
    assert events == [] and result == {}


async def test_first_attempt_pass_delivers(monkeypatch):
    events, result, calls = await run_branch(monkeypatch, SIM_INTENT, [GOOD_HTML], [passed()])
    assert stages(events) == ["planning", "generating", "verifying", "postprocessing"]
    done = events[-1]
    assert isinstance(done, ArtifactDonePayload)
    assert "Content-Security-Policy" in done.html
    assert result["retry_count"] == 0
    assert result["verification_report"]["verdict"] == "pass"
    assert calls == [None]  # no revision issues on first attempt


async def test_fail_then_pass_revises_once(monkeypatch):
    events, result, calls = await run_branch(
        monkeypatch, SIM_INTENT, [GOOD_HTML, GOOD_HTML], [failed(), passed()]
    )
    assert stages(events) == [
        "planning", "generating", "verifying", "revising", "verifying", "postprocessing",
    ]
    assert isinstance(events[-1], ArtifactDonePayload)
    assert result["retry_count"] == 1
    assert calls[0] is None
    assert calls[1] and "wrong sign on g" in calls[1][0]  # issues fed back


async def test_three_fails_degrades(monkeypatch):
    events, result, calls = await run_branch(
        monkeypatch, SIM_INTENT, [GOOD_HTML], [failed(), failed(), failed()]
    )
    last = events[-1]
    assert isinstance(last, ArtifactFailedPayload)
    assert last.reason == "verification_failed"
    assert last.retryable is True
    assert len(calls) == 3  # initial + 2 retries, never more
    assert not any(isinstance(e, ArtifactDonePayload) for e in events)
    assert result["verification_report"]["verdict"] == "fail"


async def test_postprocess_reject_counts_as_retry(monkeypatch):
    # Verifier passes both attempts, but attempt 1's html is hostile: the
    # post-processor rejects it, which must consume a retry and feed a
    # revision, not deliver (SECURITY.md section 3).
    events, result, calls = await run_branch(
        monkeypatch, SIM_INTENT, [HOSTILE_HTML, GOOD_HTML], [passed(), passed()]
    )
    assert "revising" in stages(events)
    done = events[-1]
    assert isinstance(done, ArtifactDonePayload)
    assert "fetch(" not in done.html
    assert result["retry_count"] == 1
    assert calls[1] and "Post-processor rejected" in calls[1][0]


async def test_verifier_node_error_degrades(monkeypatch):
    events, _, _ = await run_branch(
        monkeypatch, SIM_INTENT, [GOOD_HTML], [NodeError("verifier", "unparseable verdict")]
    )
    last = events[-1]
    assert isinstance(last, ArtifactFailedPayload)
    assert last.reason == "verifier_failed"


async def test_artifacts_disabled_kill_switch(monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DISABLED", "true")
    config.get_settings.cache_clear()
    events, result, _ = await run_branch(monkeypatch, SIM_INTENT, [GOOD_HTML], [passed()])
    assert events == [] and result == {}
