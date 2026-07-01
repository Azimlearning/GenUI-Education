"""Tutor Loop (PRD §5.4) — close the loop back to the persistent learner model.

P0: on composing a misconception-correcting component, record the misconception against the
learner profile and schedule a spaced-repetition review. The richer loop (watching live
interaction events — predictions, slider values, quiz answers — to update mastery) arrives in
P3 when the component streams events back. Deterministic; no LLM.

LangGraph contract: read `state`, return a partial update dict.
"""

from __future__ import annotations

from typing import Any

from app.models import AgentName, AgentStatus, DiagnosisKind, PipelineState, step
from app.store import get_store


def close_loop(state: PipelineState) -> dict[str, Any]:
    diagnosis = state.diagnosis
    if diagnosis is None or state.student_id is None:
        return {
            "steps": [
                step(
                    AgentName.tutor_loop,
                    AgentStatus.skipped,
                    "No learner profile to update (anonymous session).",
                )
            ]
        }

    steps = [step(AgentName.tutor_loop, AgentStatus.thinking, "Updating the learner profile…")]

    store = get_store()
    if diagnosis.kind == DiagnosisKind.misconception and diagnosis.misconception_id:
        store.record_misconception(
            state.student_id, diagnosis.misconception_id, diagnosis.topic, review_in_days=3
        )
        steps.append(
            step(
                AgentName.tutor_loop,
                AgentStatus.done,
                f"Logged “{diagnosis.misconception_id}” to the profile · resurface for review in 3 days.",
            )
        )
    else:
        profile = store.get(state.student_id)
        profile.mastery.setdefault(diagnosis.topic, 0.0)
        store.save(profile)
        steps.append(
            step(
                AgentName.tutor_loop,
                AgentStatus.done,
                f"Noted engagement with {diagnosis.topic} on the profile.",
            )
        )
    return {"steps": steps}
