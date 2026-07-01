"""P0 smoke tests for the scripted pipeline. Run: `uv run pytest` (needs langgraph installed)."""

from __future__ import annotations

from app.agents.graph import run_pipeline
from app.models import DiagnosisKind


def test_osmosis_misconception_flows_to_a_sandbox() -> None:
    state = run_pipeline(
        "osmosis is when water moves to where there's more water", student_id="s1"
    )

    assert state.diagnosis is not None
    assert state.diagnosis.kind == DiagnosisKind.misconception
    assert state.diagnosis.misconception_id == "osmosis-inverted-gradient"

    assert state.strategy is not None
    assert state.strategy.target_pattern == "gradient-diffusion-sandbox"

    assert state.block is not None
    assert state.block.pattern == "gradient-diffusion-sandbox"
    assert state.block.props["correct_direction"] == "toward-higher-solute"

    # Visible reasoning accumulated across all four agents.
    agents_that_spoke = {s.agent for s in state.steps}
    assert len(agents_that_spoke) == 4


def test_unknown_question_falls_back_to_knowledge_gap() -> None:
    state = run_pipeline("what is the capital of Malaysia?")
    assert state.diagnosis is not None
    assert state.diagnosis.kind == DiagnosisKind.knowledge_gap
    assert state.block is not None  # still composes something (quick-check fallback)
