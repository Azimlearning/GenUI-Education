"""Component Composer (PRD §5.3) — select + configure a component from the registry.

LIVE (P1): the model configures the chosen pattern's props (D-01 — it configures a pre-built
component, it never emits markup). We validate the props against the registry schema and, for
science-critical patterns, PIN the faithful fields in code so a wrong model answer can't ship a
wrong sim (constraint #6). SCRIPTED (P0 fallback): hand-authored presets.

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
from app.providers.router import get_router

# Faithful, science-checked fields that MUST hold regardless of what the model proposes
# (constraint #6). Merged OVER the model's props for the matching pattern.
_FAITHFUL_PINS: dict[str, dict[str, Any]] = {
    "gradient-diffusion-sandbox": {
        "particle": "water",
        "membrane": "selectively-permeable",
        "correct_direction": "toward-higher-solute",
    },
}


def _scripted_props(pattern: str) -> dict[str, Any]:
    """Hand-authored prop presets keyed by pattern (the flagship osmosis path is faithful)."""
    if pattern == "gradient-diffusion-sandbox":
        return {
            "particle": "water",
            "left_concentration": 20,
            "right_concentration": 70,
            "membrane": "selectively-permeable",
            "predict_prompt": "Which way will the water move?",
            "correct_direction": "toward-higher-solute",
            "cell_mode": "beaker",
        }
    if pattern == "force-motion-sim":
        return {
            "mass": 2,
            "applied_force": 12,
            "friction": 0.2,
            "predict_prompt": "Release the trolley — will it speed up, hold steady, or stay still?",
            "show_graph": "v-t",
        }
    if pattern == "electron-bonding-explorer":
        return {
            "pairs": [
                {"left": "Na", "right": "Cl", "formula": "NaCl"},
                {"left": "H", "right": "O", "formula": "H₂O"},
            ],
            "mode": "contrast",
        }
    if pattern == "labelled-diagram-explorer":
        return {"diagram": "animal-cell", "parts": [], "mode": "explore"}
    if pattern == "quick-check-quiz":
        return {"prompt": "Balance: H2 + O2 -> H2O", "answer_type": "coefficients",
                "correct": [2, 1, 2]}
    return {}


def _live_props(state: PipelineState, pattern_id: str, prop_schema: dict[str, str]) -> dict[str, Any]:
    diagnosis = state.diagnosis
    strategy = state.strategy
    assert diagnosis is not None and strategy is not None
    schema_lines = "\n".join(f'  "{k}": {v}' for k, v in prop_schema.items())
    prompt = (
        f"Configure a “{pattern_id}” for topic “{diagnosis.topic}” "
        f"(technique: {strategy.technique.value}).\n"
        f"Props this component accepts:\n{{\n{schema_lines}\n}}\n\n"
        "Return a JSON object of props. Keep it scientifically correct and pitched at a Form "
        f"{diagnosis.form} {diagnosis.subject} SPM student."
    )
    raw = get_router().run_structured(
        AgentName.component_composer,
        prompt,
        system="You configure pre-built KSSM science components. Output only valid props.",
        schema_hint="{ " + ", ".join(f'"{k}": ...' for k in prop_schema) + " }",
    )
    # Keep only recognised keys, then pin the faithful fields.
    props = {k: v for k, v in raw.items() if k in prop_schema}
    if not props:
        raise ValueError("model returned no recognised props")
    props.update(_FAITHFUL_PINS.get(pattern_id, {}))
    return props


def compose(state: PipelineState) -> dict[str, Any]:
    strategy = state.strategy
    diagnosis = state.diagnosis
    if strategy is None or diagnosis is None:
        return {
            "steps": [
                step(AgentName.component_composer, AgentStatus.skipped,
                     "Missing strategy/diagnosis — nothing to compose.")
            ]
        }

    steps = [
        step(AgentName.component_composer, AgentStatus.thinking,
             f"Selecting and configuring a “{strategy.target_pattern}”…")
    ]

    pattern = get_pattern(strategy.target_pattern)
    pattern_id = pattern.pattern if pattern else "quick-check-quiz"

    router = get_router()
    props: dict[str, Any] | None = None
    if pattern is not None and router.any_live(AgentName.component_composer):
        try:
            props = _live_props(state, pattern_id, pattern.prop_schema)
        except Exception:  # noqa: BLE001 - any live failure falls back to scripted presets
            props = None
    if props is None:
        props = _scripted_props(pattern_id)
        # Faithful pins apply to scripted props too (belt and braces).
        props.update(_FAITHFUL_PINS.get(pattern_id, {}))

    block = ComponentBlock(
        pattern=pattern_id,
        props=props,
        meta=BlockMeta(
            subject=diagnosis.subject,
            form=diagnosis.form,
            topic=diagnosis.topic,
            strategy=strategy.technique,
            misconception_id=diagnosis.misconception_id,
        ),
    )
    steps.append(
        step(AgentName.component_composer, AgentStatus.done,
             f"Composed a “{pattern_id}” configured for {diagnosis.topic}.")
    )
    return {"block": block, "steps": steps}
