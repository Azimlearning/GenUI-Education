"""Diagnostician (PRD §5.1) — identify the student's conceptual state.

Two paths, same output contract:

- LIVE (P1): classify the question via the provider router, GROUNDED in the misconception KB —
  the model must pick a `misconception_id` from the list we pass it, never invent one (D-04).
- SCRIPTED (P0 fallback): keyword match against the KB, used when no provider is configured or
  the model's answer fails validation. The demo always runs.

LangGraph contract: read `state`, return a partial update dict. `steps` is concatenated by the
reducer (see PipelineState), so return only the steps THIS node produced.
"""

from __future__ import annotations

from typing import Any

from app.knowledge import MISCONCEPTIONS, detect, get_misconception
from app.models import (
    AgentName,
    AgentStatus,
    Diagnosis,
    DiagnosisKind,
    PipelineState,
    step,
)
from app.providers.router import get_router

# Very light P0 subject/topic guesser for the scripted no-misconception path.
_SUBJECT_HINTS: list[tuple[tuple[str, ...], str, str]] = [
    (("cell", "organelle", "nucleus", "mitochond"), "Biology", "cell structure"),
    (("bond", "ionic", "covalent", "electron"), "Chemistry", "chemical bonding"),
    (("balanc", "equation", "mole", "stoichio"), "Chemistry", "chemical equations"),
    (("force", "motion", "newton", "velocity", "momentum"), "Physics", "forces and motion"),
    (("osmos", "diffus", "water"), "Biology", "movement of substances"),
]

_DIAGNOSIS_SHAPE = (
    '{"kind": "misconception|knowledge_gap|mastery_check", "subject": "Biology|Chemistry|Physics",'
    ' "form": 4 or 5, "topic": "short topic label", '
    '"misconception_id": "one id from the candidate list, or null", '
    '"summary": "one sentence for the student-facing pipeline", "confidence": 0.0-1.0}'
)


def _guess_subject_topic(question: str) -> tuple[str, str]:
    q = question.lower()
    for cues, subject, topic in _SUBJECT_HINTS:
        if any(c in q for c in cues):
            return subject, topic
    return "Science", "general enquiry"


def _scripted_diagnose(question: str) -> Diagnosis:
    m = detect(question)
    if m is not None:
        return Diagnosis(
            kind=DiagnosisKind.misconception,
            subject=m.subject,
            form=m.form,
            topic=m.topic,
            misconception_id=m.id,
            summary=f"Detected a common misconception: “{m.statement}”",
            confidence=0.9,
        )
    subject, topic = _guess_subject_topic(question)
    return Diagnosis(
        kind=DiagnosisKind.knowledge_gap,
        subject=subject,
        form=4,
        topic=topic,
        summary=f"No specific misconception matched — treating as a knowledge gap in {topic}.",
        confidence=0.5,
    )


def _candidate_block() -> str:
    """The grounding: every KB misconception the model is allowed to choose from."""
    lines = []
    for m in MISCONCEPTIONS.values():
        lines.append(
            f'- id="{m.id}" ({m.subject}, Form {m.form}, {m.topic}): '
            f'students think "{m.statement}"'
        )
    return "\n".join(lines)


def _live_diagnose(question: str) -> Diagnosis:
    """Classify via the router; raises ProviderUnavailable / ValueError on any failure."""
    prompt = (
        f"A Malaysian KSSM SPM science student wrote:\n“{question}”\n\n"
        "Candidate misconceptions (choose misconception_id ONLY from these ids):\n"
        f"{_candidate_block()}\n\n"
        "If the student's statement matches one of these misconceptions, set kind=misconception "
        "and misconception_id to its id. If they just lack knowledge, kind=knowledge_gap with "
        "misconception_id null. If they seem to understand and want to check, kind=mastery_check."
    )
    raw = get_router().run_structured(
        AgentName.diagnostician,
        prompt,
        system="You are a KSSM SPM science diagnostician. Classify, never invent misconceptions.",
        schema_hint=_DIAGNOSIS_SHAPE,
    )
    kind = DiagnosisKind(str(raw["kind"]))
    mid = raw.get("misconception_id")
    if kind == DiagnosisKind.misconception:
        # Grounding gate: the id MUST exist in the KB, else this isn't a real diagnosis.
        m = get_misconception(str(mid)) if mid else None
        if m is None:
            raise ValueError(f"model returned unknown misconception_id={mid!r}")
        return Diagnosis(
            kind=kind, subject=m.subject, form=m.form, topic=m.topic,
            misconception_id=m.id,
            summary=str(raw.get("summary") or f"Common misconception: {m.statement}"),
            confidence=float(raw.get("confidence", 0.85)),
        )
    return Diagnosis(
        kind=kind,
        subject=str(raw.get("subject", "Science")),
        form=int(raw.get("form", 4)),
        topic=str(raw.get("topic", "general enquiry")),
        misconception_id=None,
        summary=str(raw.get("summary") or "Treating this as a knowledge gap."),
        confidence=float(raw.get("confidence", 0.6)),
    )


def diagnose(state: PipelineState) -> dict[str, Any]:
    steps = [step(AgentName.diagnostician, AgentStatus.thinking, "Understanding the question…")]

    router = get_router()
    diagnosis: Diagnosis | None = None
    if router.any_live(AgentName.diagnostician):
        try:
            diagnosis = _live_diagnose(state.question)
        except Exception:  # noqa: BLE001 - any live failure falls back to scripted
            diagnosis = None
    if diagnosis is None:
        diagnosis = _scripted_diagnose(state.question)

    if diagnosis.kind == DiagnosisKind.misconception:
        detail = (
            f"Misconception detected — {diagnosis.misconception_id} "
            f"({diagnosis.subject}, Form {diagnosis.form})."
        )
    else:
        detail = f"{diagnosis.kind.value.replace('_', ' ').title()} in {diagnosis.topic} ({diagnosis.subject})."
    steps.append(step(AgentName.diagnostician, AgentStatus.done, detail))
    return {"diagnosis": diagnosis, "steps": steps}
