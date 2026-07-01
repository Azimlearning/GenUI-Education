"""Pedagogy Strategist (PRD §5.2) — pick the learning-science-correct intervention.

LIVE (P1): reason over the diagnosis via the router to choose a technique + target pattern,
naming the learning-science rationale. SCRIPTED (P0 fallback): the diagnosis-kind heuristic.
Either way the chosen `target_pattern` must be a real registry pattern (validated).

LangGraph contract: read `state`, return a partial update dict.
"""

from __future__ import annotations

from typing import Any

from app.components import REGISTRY, find_pattern_for
from app.models import (
    AgentName,
    AgentStatus,
    DiagnosisKind,
    PipelineState,
    Strategy,
    Technique,
    step,
)
from app.providers.router import get_router

# Diagnosis kind → the default pedagogical move (scripted heuristic; PRD §7 lists the full set).
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

_STRATEGY_SHAPE = (
    '{"technique": "predict-observe-explain|contrasting-cases|worked-example-fading|'
    'retrieval-practice|labelled-exploration", "target_pattern": "a component pattern id", '
    '"rationale": "one sentence naming the learning-science reason"}'
)


def _scripted_strategy(state: PipelineState) -> Strategy:
    diagnosis = state.diagnosis
    assert diagnosis is not None
    technique = _KIND_TO_TECHNIQUE.get(diagnosis.kind, Technique.predict_observe_explain)
    pattern = find_pattern_for(diagnosis.topic, technique)
    # For a topic with a sandbox, predict-observe-explain is the strongest move.
    if pattern is not None and Technique.predict_observe_explain in pattern.techniques:
        technique = Technique.predict_observe_explain
    target_pattern = pattern.pattern if pattern else "quick-check-quiz"
    return Strategy(technique=technique, target_pattern=target_pattern,
                    rationale=_RATIONALE[technique])


def _live_strategy(state: PipelineState) -> Strategy:
    diagnosis = state.diagnosis
    assert diagnosis is not None
    # Offer the model the patterns that plausibly serve this topic, plus the always-available quiz.
    suggested = find_pattern_for(diagnosis.topic)
    pattern_hint = ", ".join(
        sorted({p for p in ([suggested.pattern] if suggested else []) + list(REGISTRY.keys())})
    )
    prompt = (
        f"Diagnosis: kind={diagnosis.kind.value}, subject={diagnosis.subject}, "
        f"topic={diagnosis.topic}, misconception_id={diagnosis.misconception_id}.\n"
        f"Available component patterns: {pattern_hint}.\n\n"
        "Choose the pedagogically-correct intervention. For a misconception, prefer "
        "predict-observe-explain via a sandbox so the wrong idea fails visibly. Name the "
        "learning-science technique and the target_pattern the Composer should build."
    )
    raw = get_router().run_structured(
        AgentName.pedagogy_strategist,
        prompt,
        system="You are a learning-science strategist for KSSM SPM science.",
        schema_hint=_STRATEGY_SHAPE,
    )
    technique = Technique(str(raw["technique"]))
    target_pattern = str(raw["target_pattern"])
    if target_pattern not in REGISTRY:
        raise ValueError(f"unknown target_pattern={target_pattern!r}")
    rationale = str(raw.get("rationale") or _RATIONALE.get(technique, ""))
    return Strategy(technique=technique, target_pattern=target_pattern, rationale=rationale)


def strategize(state: PipelineState) -> dict[str, Any]:
    if state.diagnosis is None:  # defensive — graph order guarantees this is set
        return {
            "steps": [
                step(AgentName.pedagogy_strategist, AgentStatus.skipped,
                     "No diagnosis to strategise from.")
            ]
        }

    steps = [
        step(AgentName.pedagogy_strategist, AgentStatus.thinking,
             "Choosing the pedagogically-correct move…")
    ]

    router = get_router()
    strategy: Strategy | None = None
    if router.any_live(AgentName.pedagogy_strategist):
        try:
            strategy = _live_strategy(state)
        except Exception:  # noqa: BLE001 - any live failure falls back to scripted
            strategy = None
    if strategy is None:
        strategy = _scripted_strategy(state)

    steps.append(
        step(AgentName.pedagogy_strategist, AgentStatus.done,
             f"{strategy.technique.value} → compose a “{strategy.target_pattern}”. {strategy.rationale}")
    )
    return {"strategy": strategy, "steps": steps}
