"""Component Composer (PRD §5.3) — select + configure a component from the registry.

P0: emits a hand-configured `ComponentBlock` for the known patterns (osmosis sandbox etc.),
using the strategy's `target_pattern`. P1: props are generated via the provider router, still
validated against the registry's `prop_schema` (the model configures a pre-built component — it
never invents markup, D-01).

LangGraph contract: read `state`, return a partial update dict.
"""

from __future__ import annotations

from typing import Any

from app.components import get_pattern
from app.models import (
    AgentName,
    AgentStatus,
    BlockMeta,
    ComponentBlock,
    PipelineState,
    step,
)


def _props_for(pattern: str) -> dict[str, Any]:
    """P0 hand-authored prop presets keyed by pattern (the flagship osmosis path is faithful)."""
    if pattern == "gradient-diffusion-sandbox":
        return {
            "particle": "water",
            "left_concentration": 20,
            "right_concentration": 70,
            "membrane": "selectively-permeable",
            "predict_prompt": "Which way will the water move?",
            "correct_direction": "toward-higher-solute",
        }
    if pattern == "contrasting-pair-walkthrough":
        return {
            "left_label": "Ionic",
            "right_label": "Covalent",
            "criteria": ["electron behaviour", "elements involved", "electronegativity difference"],
            "examples": [
                {"formula": "NaCl", "answer": "Ionic"},
                {"formula": "H2O", "answer": "Covalent"},
            ],
        }
    if pattern == "labelled-diagram-explorer":
        return {"diagram": "animal-cell", "parts": [], "mode": "explore"}
    if pattern == "quick-check-quiz":
        return {"prompt": "Balance: H2 + O2 -> H2O", "answer_type": "coefficients", "correct": [2, 1, 2]}
    return {}


def compose(state: PipelineState) -> dict[str, Any]:
    strategy = state.strategy
    diagnosis = state.diagnosis
    if strategy is None or diagnosis is None:
        return {
            "steps": [
                step(
                    AgentName.component_composer,
                    AgentStatus.skipped,
                    "Missing strategy/diagnosis — nothing to compose.",
                )
            ]
        }

    steps = [
        step(
            AgentName.component_composer,
            AgentStatus.thinking,
            f"Selecting and configuring a “{strategy.target_pattern}”…",
        )
    ]

    pattern = get_pattern(strategy.target_pattern)
    pattern_id = pattern.pattern if pattern else "quick-check-quiz"

    block = ComponentBlock(
        pattern=pattern_id,
        props=_props_for(pattern_id),
        meta=BlockMeta(
            subject=diagnosis.subject,
            form=diagnosis.form,
            topic=diagnosis.topic,
            strategy=strategy.technique,
            misconception_id=diagnosis.misconception_id,
        ),
    )
    steps.append(
        step(
            AgentName.component_composer,
            AgentStatus.done,
            f"Composed a “{pattern_id}” configured for {diagnosis.topic}.",
        )
    )
    return {"block": block, "steps": steps}
