"""P1 tests — the live-slice machinery that P0 didn't cover.

These exercise the pieces that make the osmosis slice real: JSON extraction + repair in the
router, the faithful-props gate in the Composer, SSE serialisation, the SQLite learner store,
and cost estimation. They run without any API key (the LLM paths fall back to scripted).
"""

from __future__ import annotations

import json

from app.agents.graph import run_pipeline
from app.api.routes import _sse
from app.models import AgentStep, AgentName, AgentStatus, ComponentEvent, DoneEvent
from app.providers.metrics import estimate_cost
from app.providers.router import _extract_json
from app.store.learner_store import SqliteLearnerStore


# ── Router JSON extraction ──────────────────────────────────────────────────
def test_extract_json_plain() -> None:
    assert _extract_json('{"a": 1, "b": "x"}') == {"a": 1, "b": "x"}


def test_extract_json_strips_fences_and_prose() -> None:
    text = 'Sure! Here is the object:\n```json\n{"kind": "misconception"}\n```\nHope that helps.'
    assert _extract_json(text) == {"kind": "misconception"}


def test_extract_json_returns_none_on_garbage() -> None:
    assert _extract_json("no json here at all") is None
    assert _extract_json("") is None


# ── Composer faithfulness gate (constraint #6) ──────────────────────────────
def test_osmosis_block_is_scientifically_faithful() -> None:
    state = run_pipeline("osmosis is when water moves to where there's more water", student_id="s1")
    assert state.block is not None
    assert state.block.pattern == "gradient-diffusion-sandbox"
    # The science-critical field is pinned regardless of provider.
    assert state.block.props["correct_direction"] == "toward-higher-solute"
    assert state.block.props["particle"] == "water"
    assert state.block.props["membrane"] == "selectively-permeable"


# ── SSE serialisation (the D-10 wire seam) ──────────────────────────────────
def test_sse_serialises_each_event_type() -> None:
    step_ev = AgentStep(agent=AgentName.diagnostician, status=AgentStatus.done, detail="hi")
    frame = _sse(step_ev)
    assert frame["event"] == "agent_step"
    assert json.loads(frame["data"])["detail"] == "hi"

    done = _sse(DoneEvent())
    assert done["event"] == "done"

    state = run_pipeline("osmosis moves to more water", student_id="s2")
    assert state.block is not None
    comp = _sse(ComponentEvent(block=state.block))
    assert comp["event"] == "component_block"
    assert json.loads(comp["data"])["block"]["pattern"] == "gradient-diffusion-sandbox"


# ── SQLite learner store (P1e) ──────────────────────────────────────────────
def test_sqlite_store_persists_and_schedules_review(tmp_path) -> None:
    path = str(tmp_path / "learners.sqlite3")
    store = SqliteLearnerStore(path)
    store.record_misconception("stu-1", "osmosis-inverted-gradient", "osmosis", review_in_days=3)

    # A fresh store over the same file sees the persisted profile (durability).
    reopened = SqliteLearnerStore(path)
    profile = reopened.get("stu-1")
    assert "osmosis-inverted-gradient" in profile.misconceptions
    obs = profile.misconceptions["osmosis-inverted-gradient"]
    assert obs.topic == "osmosis"
    assert obs.review_due is not None and obs.review_due > obs.first_seen


# ── Cost estimation ─────────────────────────────────────────────────────────
def test_cost_estimate_uses_pricing_table() -> None:
    cost = estimate_cost("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
    assert cost == 6.0  # $1 in + $5 out per 1M
    assert estimate_cost("unknown-model", 1000, 1000) == 0.0
