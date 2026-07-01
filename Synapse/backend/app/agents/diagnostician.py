"""Diagnostician (PRD §5.1) — identify the student's conceptual state.

P0: keyword-grounded stub. Detects a misconception from the KB (`knowledge.detect`) or falls
back to a knowledge-gap diagnosis with a light subject/topic guess. P1: classify via the
provider router, still selecting from the misconception KB rather than improvising (D-04).

LangGraph contract: read `state`, return a partial update dict. `steps` is concatenated by
the reducer (see PipelineState), so return only the steps THIS node produced.
"""

from __future__ import annotations

from typing import Any

from app.knowledge import detect
from app.models import (
    AgentName,
    AgentStatus,
    Diagnosis,
    DiagnosisKind,
    PipelineState,
    step,
)

# Very light P0 subject/topic guesser for the no-misconception path.
_SUBJECT_HINTS: list[tuple[tuple[str, ...], str, str]] = [
    (("cell", "organelle", "nucleus", "mitochond"), "Biology", "cell structure"),
    (("bond", "ionic", "covalent", "electron"), "Chemistry", "chemical bonding"),
    (("balanc", "equation", "mole", "stoichio"), "Chemistry", "chemical equations"),
    (("force", "motion", "newton", "velocity", "momentum"), "Physics", "forces and motion"),
    (("osmos", "diffus", "water"), "Biology", "movement of substances"),
]


def _guess_subject_topic(question: str) -> tuple[str, str]:
    q = question.lower()
    for cues, subject, topic in _SUBJECT_HINTS:
        if any(c in q for c in cues):
            return subject, topic
    return "Science", "general enquiry"


def diagnose(state: PipelineState) -> dict[str, Any]:
    steps = [step(AgentName.diagnostician, AgentStatus.thinking, "Understanding the question…")]

    m = detect(state.question)
    if m is not None:
        diagnosis = Diagnosis(
            kind=DiagnosisKind.misconception,
            subject=m.subject,
            form=m.form,
            topic=m.topic,
            misconception_id=m.id,
            summary=f"Detected a common misconception: “{m.statement}”",
            confidence=0.9,
        )
        steps.append(
            step(
                AgentName.diagnostician,
                AgentStatus.done,
                f"Misconception detected — {m.id} ({m.subject}, Form {m.form}).",
            )
        )
        return {"diagnosis": diagnosis, "steps": steps}

    subject, topic = _guess_subject_topic(state.question)
    diagnosis = Diagnosis(
        kind=DiagnosisKind.knowledge_gap,
        subject=subject,
        form=4,
        topic=topic,
        summary=f"No specific misconception matched — treating as a knowledge gap in {topic}.",
        confidence=0.5,
    )
    steps.append(
        step(AgentName.diagnostician, AgentStatus.done, f"Knowledge gap in {topic} ({subject}).")
    )
    return {"diagnosis": diagnosis, "steps": steps}
