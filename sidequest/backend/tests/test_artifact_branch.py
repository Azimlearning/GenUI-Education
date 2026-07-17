"""Artifact branch integration tests with mocked LLM nodes (EVALS.md: recorded/
mocked fixtures keep CI deterministic and free)."""

import pytest
from pydantic import BaseModel

import config
import graph.nodes.artifact as artifact_module
import graph.nodes.verifier as verifier_module
from graph.context import RunContext
from graph.errors import NodeError
from graph.nodes.artifact import artifact_branch
from schemas.events import ArtifactDonePayload, ArtifactFailedPayload, ArtifactStatusPayload
from schemas.intent import Intent
from schemas.plan import ArtifactPlan, Variable

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


async def run_branch(monkeypatch, intent, html=GOOD_HTML, generator_error=None):
    events: list[BaseModel] = []

    async def emit(payload):
        events.append(payload)

    async def fake_planner(ctx, query, artifact_type, domain):
        return PLAN

    async def fake_generator(ctx, plan, revision_issues=None):
        if generator_error:
            raise generator_error
        return html

    monkeypatch.setattr(artifact_module, "run_planner", fake_planner)
    monkeypatch.setattr(artifact_module, "run_generator", fake_generator)
    monkeypatch.setattr(artifact_module, "record_trace", _sync_noop)
    monkeypatch.setattr(verifier_module, "record_trace", _sync_noop)

    ctx = RunContext(run_id="run_test", session_id="sess_test", emit=emit)
    state = {"query": "show me projectile motion", "intent": intent, "retry_count": 0}
    result = await artifact_branch(state, {"configurable": {"ctx": ctx}})
    return events, result


async def test_text_only_intent_skips_branch(monkeypatch):
    events, result = await run_branch(monkeypatch, TEXT_INTENT)
    assert events == [] and result == {}


async def test_happy_path_emits_statuses_then_done(monkeypatch):
    events, result = await run_branch(monkeypatch, SIM_INTENT)

    stages = [e.stage for e in events if isinstance(e, ArtifactStatusPayload)]
    assert stages == ["planning", "generating", "verifying", "postprocessing"]

    done = events[-1]
    assert isinstance(done, ArtifactDonePayload)
    assert done.title == "Projectile Motion Lab"
    assert done.artifact_id.startswith("art_")
    # post-processed: CSP injected and it precedes the vendored script
    assert "Content-Security-Policy" in done.html
    assert done.html.index("Content-Security-Policy") < done.html.index("/vendor/p5.min.js")
    assert result["final_artifact_id"] == done.artifact_id


async def test_hostile_output_degrades_via_postprocess(monkeypatch):
    events, result = await run_branch(monkeypatch, SIM_INTENT, html=HOSTILE_HTML)

    failed = events[-1]
    assert isinstance(failed, ArtifactFailedPayload)
    assert failed.reason == "postprocess_reject:forbidden_api_scan"
    assert failed.retryable is True
    assert not any(isinstance(e, ArtifactDonePayload) for e in events)
    assert "fetch" in result["failure_reason"]


async def test_generator_node_error_degrades(monkeypatch):
    events, _ = await run_branch(
        monkeypatch, SIM_INTENT, generator_error=NodeError("generator", "no html")
    )
    failed = events[-1]
    assert isinstance(failed, ArtifactFailedPayload)
    assert failed.reason == "generator_failed"
    assert failed.retryable is True


async def test_artifacts_disabled_kill_switch(monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DISABLED", "true")
    config.get_settings.cache_clear()
    events, result = await run_branch(monkeypatch, SIM_INTENT)
    assert events == [] and result == {}
