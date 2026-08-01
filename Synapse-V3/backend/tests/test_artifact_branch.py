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
    study_note="Range peaks at 45 degrees because sin(2*theta) peaks there.",
)

GOOD_HTML = (
    "<!doctype html><html><head><title>t</title></head><body>"
    "<script src=\"/vendor/p5.min.js\"></script>"
    "<script>window.parent.postMessage({type:'synapse_ready'},'*');</script>"
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
KOH_INTENT = Intent(
    artifact_type='virtual_experiment', domain='chemistry', complexity=3,
    canonical_concept='acid_base_titration',
)
KOH_QUERY = (
    'Determine the concentration of potassium hydroxide solution, KOH by acid-base titration. '
    'Materials: HNO3 and KOH. Apparatus: burette, 25 cm3 pipette and conical flask.'
)
YEAST_INTENT = Intent(
    artifact_type='virtual_experiment', domain='biology', complexity=3,
    canonical_concept='yeast_fermentation_products',
)
YEAST_QUERY = 'What are the products of yeast fermentation?'


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


def failed_safety(description: str = "calls fetch") -> VerifierReport:
    return VerifierReport(
        verdict="fail",
        issues=[
            VerifierIssue(
                severity="blocker",
                category="safety",
                description=description,
                fix_hint="remove the network call",
            )
        ],
    )


def failed_interactivity(description: str = "drag target cannot be reached") -> VerifierReport:
    return VerifierReport(
        verdict="fail",
        issues=[
            VerifierIssue(
                severity="blocker",
                category="interactivity",
                description=description,
                fix_hint="wire pointer handlers and a visible target",
            )
        ],
    )


@pytest.fixture(autouse=True)
def live_mode(monkeypatch):
    """The branch requires llm_enabled; LLM calls themselves are patched out."""
    monkeypatch.setenv("ECHO_MODE", "false")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    monkeypatch.setattr(artifact_module, "BUILTIN_STAGE_DELAY_S", 0)  # no real waits in tests
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


def _sync_noop(*args, **kwargs):
    return None


async def run_branch(monkeypatch, intent, htmls, verdicts, query='show me projectile motion'):
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
        outcome = htmls[min(retry_index, len(htmls) - 1)]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    async def fake_verifier(ctx, plan, html, retry_index=0):
        outcome = verdicts[min(retry_index, len(verdicts) - 1)]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(artifact_module, "run_planner", fake_planner)
    monkeypatch.setattr(artifact_module, "run_generator", fake_generator)
    monkeypatch.setattr(artifact_module, "run_verifier", fake_verifier)
    monkeypatch.setattr(artifact_module, "record_trace", _sync_noop)
    monkeypatch.setattr(verifier_module, "record_trace", _sync_noop)

    ctx = RunContext(run_id="run_test", session_id="sess_test", emit=emit)
    state = {"query": query, "intent": intent, "retry_count": 0}
    result = await artifact_branch(state, {"configurable": {"ctx": ctx}})
    return events, result, generator_calls


def stages(events):
    return [e.stage for e in events if isinstance(e, ArtifactStatusPayload)]


async def test_text_only_intent_skips_branch(monkeypatch):
    events, result, _ = await run_branch(monkeypatch, TEXT_INTENT, [GOOD_HTML], [passed()])
    assert events == [] and result == {}


async def test_explicit_koh_brief_delivers_the_builtin_lab_without_generation(monkeypatch):
    events, result, calls = await run_branch(
        monkeypatch, KOH_INTENT, [GOOD_HTML], [passed()], query=KOH_QUERY
    )
    assert stages(events) == ['planning', 'generating', 'verifying', 'postprocessing']
    done = events[-1]
    assert isinstance(done, ArtifactDonePayload)
    assert done.verified is True
    assert 'swirl_mix' in done.html
    assert 'setPointerCapture' in done.html
    assert calls == []
    assert result['verification_report']['verdict'] == 'pass'


async def test_yeast_products_brief_delivers_the_builtin_lab_without_generation(monkeypatch):
    events, result, calls = await run_branch(
        monkeypatch, YEAST_INTENT, [GOOD_HTML], [passed()], query=YEAST_QUERY
    )
    assert stages(events) == ['planning', 'generating', 'verifying', 'postprocessing']
    done = events[-1]
    assert isinstance(done, ArtifactDonePayload)
    assert done.verified is True
    assert 'add_yeast_to_tube_a' in done.html
    assert 'incubation_minutes' in done.html
    assert calls == []
    assert result['verification_report']['verdict'] == 'pass'


async def test_supported_builtin_survives_an_upstream_text_only_misroute(monkeypatch):
    events, result, calls = await run_branch(
        monkeypatch, TEXT_INTENT, [GOOD_HTML], [passed()], query=YEAST_QUERY
    )
    assert isinstance(events[-1], ArtifactDonePayload)
    assert events[-1].verified is True
    assert calls == []
    assert result['final_artifact_id']


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


async def test_three_accuracy_fails_delivers_unverified(monkeypatch):
    # Accuracy-only failure (safe html, no safety issue): after retries the
    # branch shows the work with verified=False instead of degrading to text
    # (user-approved 2026-07-18). Safety hardening still runs on the fallback.
    events, result, calls = await run_branch(
        monkeypatch, SIM_INTENT, [GOOD_HTML], [failed(), failed(), failed()]
    )
    done = events[-1]
    assert isinstance(done, ArtifactDonePayload)
    assert done.verified is False
    assert "Content-Security-Policy" in done.html  # postprocess still applied
    assert len(calls) == 4  # initial + 3 retries, never more
    assert result["unverified"] is True
    assert result["verification_report"]["verdict"] == "fail"


async def test_three_safety_fails_degrades(monkeypatch):
    # A safety-category failure must NEVER be shown, even unverified: degrade
    # to text. This is the security half of the accuracy/safety split.
    events, result, calls = await run_branch(
        monkeypatch, SIM_INTENT, [GOOD_HTML], [failed_safety(), failed_safety(), failed_safety()]
    )
    last = events[-1]
    assert isinstance(last, ArtifactFailedPayload)
    assert last.reason == "verification_failed"
    assert not any(isinstance(e, ArtifactDonePayload) for e in events)
    assert result.get("unverified") is None


async def test_three_interactivity_fails_degrade_instead_of_showing_broken_lab(monkeypatch):
    # A draft with dead drag/drop controls is not useful to a learner. The
    # branch must degrade to text after revisions, just as it does for safety.
    events, result, _ = await run_branch(
        monkeypatch,
        SIM_INTENT,
        [GOOD_HTML],
        [failed_interactivity(), failed_interactivity(), failed_interactivity()],
    )
    last = events[-1]
    assert isinstance(last, ArtifactFailedPayload)
    assert last.reason == "verification_failed"
    assert not any(isinstance(e, ArtifactDonePayload) for e in events)
    assert result.get("unverified") is None


async def test_generator_errors_do_not_claim_a_science_check(monkeypatch):
    events, result, calls = await run_branch(
        monkeypatch,
        SIM_INTENT,
        [NodeError("generator", "empty response (stop_reason='max_tokens')")],
        [passed()],
    )
    last = events[-1]
    assert isinstance(last, ArtifactFailedPayload)
    assert "did not return a complete interactive document" in last.detail_user
    assert "science check" not in last.detail_user
    assert len(calls) == 4
    assert result["failure_reason"] == "verification_failed"


async def test_unverified_fallback_blocked_by_hostile_html(monkeypatch):
    # Non-safety verdict, but the html itself is hostile: the fallback's
    # postprocess re-scan rejects it, so it degrades to text rather than
    # rendering unsafe code with a note.
    events, result, _ = await run_branch(
        monkeypatch, SIM_INTENT, [HOSTILE_HTML], [failed(), failed(), failed()]
    )
    last = events[-1]
    assert isinstance(last, ArtifactFailedPayload)
    assert not any(isinstance(e, ArtifactDonePayload) for e in events)


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
