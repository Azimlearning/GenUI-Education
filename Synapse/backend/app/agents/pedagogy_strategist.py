"""Pedagogy Strategist (PRD §5.2) — pick the learning-science-correct intervention.

P0: rule-of-thumb mapping from diagnosis → technique + a target component pattern (using the
registry to find a pattern that serves the topic). P1: reason via the provider router over the
diagnosis + learner history to choose the technique.

LangGraph contract: read `state`, return a partial update dict.
"""

from __future__ import annotations

from typing import Any

from app.components import find_pattern_for
from app.models import (
    AgentName,
    AgentStatus,
    DiagnosisKind,
    PipelineState,
    Strategy,
    Technique,
    step,
)

# Diagnosis kind → the default pedagogical move (P0 heuristic; PRD §7 lists the full set).
_KIND_TO_TECHNIQUE: dict[DiagnosisKind, Technique] = {
    DiagnosisKind.misconception: Technique.contrasting_cases,
    DiagnosisKind.knowledge_gap: Technique.worked_example_fading,
    DiagnosisKind.mastery_check: Technique.retrieval_practice,
}

_RATIONALE: dict[Technique, str] = {
    Technique.contrasting_cases: (
        "It's a misconception, not a gap — don't explain; contrast cases so the wrong idea "
        "fails visibly."
    ),
    Technique.predict_observe_explain: (
        "Make the student commit to a prediction, then let the simulation contradict it — the "
        "contradiction is the teaching moment."
    ),
    Technique.worked_example_fading: (
        "Fill the gap with a worked example that fades support as they follow along."
    ),
    Technique.retrieval_practice: "Test recall to consolidate and check mastery.",
    Technique.labelled_exploration: "Let them explore and label the structure directly.",
}


def strategize(state: PipelineState) -> dict[str, Any]:
    diagnosis = state.diagnosis
    if diagnosis is None:  # defensive — graph order guarantees this is set
        return {
            "steps": [
                step(
                    AgentName.pedagogy_strategist,
                    AgentStatus.skipped,
                    "No diagnosis to strategise from.",
                )
            ]
        }

    steps = [
        step(
            AgentName.pedagogy_strategist,
            AgentStatus.thinking,
            "Choosing the pedagogically-correct move…",
        )
    ]

    technique = _KIND_TO_TECHNIQUE.get(diagnosis.kind, Technique.predict_observe_explain)

    # For a misconception, the strongest move is predict-observe-explain via a sandbox when the
    # topic has one — otherwise keep contrasting cases.
    pattern = find_pattern_for(diagnosis.topic, technique)
    if pattern is not None and Technique.predict_observe_explain in pattern.techniques:
        technique = Technique.predict_observe_explain

    target_pattern = pattern.pattern if pattern else "quick-check-quiz"
    rationale = _RATIONALE[technique]

    strategy = Strategy(technique=technique, target_pattern=target_pattern, rationale=rationale)
    steps.append(
        step(
            AgentName.pedagogy_strategist,
            AgentStatus.done,
            f"{technique.value} → compose a “{target_pattern}”. {rationale}",
        )
    )
    return {"strategy": strategy, "steps": steps}
