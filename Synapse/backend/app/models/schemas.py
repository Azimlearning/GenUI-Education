"""The typed SSE contract and shared pipeline state (ADR-010 — the load-bearing seam).

Anything here that describes a wire event MUST stay in sync with the frontend mirror
`frontend/lib/blocks.ts` / `frontend/lib/types.ts`. Treat a change to a wire model and
its TS mirror as a single change (D-10).
"""

from __future__ import annotations

import operator
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class AgentName(str, Enum):
    diagnostician = "diagnostician"
    pedagogy_strategist = "pedagogy_strategist"
    component_composer = "component_composer"
    tutor_loop = "tutor_loop"


class AgentStatus(str, Enum):
    thinking = "thinking"
    done = "done"
    skipped = "skipped"


class DiagnosisKind(str, Enum):
    misconception = "misconception"
    knowledge_gap = "knowledge_gap"
    mastery_check = "mastery_check"


class Technique(str, Enum):
    """Learning-science interventions the Strategist may choose (PRD §7)."""

    contrasting_cases = "contrasting-cases"
    predict_observe_explain = "predict-observe-explain"
    worked_example_fading = "worked-example-fading"
    retrieval_practice = "retrieval-practice"
    labelled_exploration = "labelled-exploration"


# ─────────────────────────────────────────────────────────────────────────────
# Agent outputs
# ─────────────────────────────────────────────────────────────────────────────


class Diagnosis(BaseModel):
    """Output of the Diagnostician (PRD §5.1)."""

    kind: DiagnosisKind
    subject: str  # "Biology" | "Chemistry" | "Physics"
    form: int = Field(ge=4, le=5)
    topic: str  # e.g. "osmosis"
    misconception_id: str | None = None  # key into the misconception KB, when kind == misconception
    summary: str  # human-readable, streamed to the visible pipeline
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class Strategy(BaseModel):
    """Output of the Pedagogy Strategist (PRD §5.2)."""

    technique: Technique
    target_pattern: str  # a component-registry pattern id the Composer should use
    rationale: str  # streamed to the visible pipeline


# ─────────────────────────────────────────────────────────────────────────────
# The component block (Composer output → SSE → frontend library)
# ─────────────────────────────────────────────────────────────────────────────


class BlockMeta(BaseModel):
    subject: str
    form: int
    topic: str
    strategy: Technique
    misconception_id: str | None = None


class ComponentBlock(BaseModel):
    """A typed, parameterised instruction to render a pre-built component (ADR-010).

    `pattern` keys into the frontend library (`frontend/lib/blocks.ts`); `props` are
    validated pattern-specific parameters; `meta` carries pedagogical context for the UI.
    The backend never sends markup — only which component and how to configure it (D-01).
    """

    pattern: str
    props: dict[str, Any] = Field(default_factory=dict)
    meta: BlockMeta


# ─────────────────────────────────────────────────────────────────────────────
# SSE events (the wire protocol for POST /api/ask)
# ─────────────────────────────────────────────────────────────────────────────


class AgentStep(BaseModel):
    """One reasoning step, streamed so the UI can show the pipeline thinking live (D-03)."""

    type: Literal["agent_step"] = "agent_step"
    agent: AgentName
    status: AgentStatus
    detail: str  # what this agent concluded / is doing, in plain language


class ComponentEvent(BaseModel):
    """Wraps a ComponentBlock as an SSE event."""

    type: Literal["component_block"] = "component_block"
    block: ComponentBlock


class DoneEvent(BaseModel):
    type: Literal["done"] = "done"


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str


# Discriminated union of everything that can go over the wire.
SSEEvent = AgentStep | ComponentEvent | DoneEvent | ErrorEvent


# ─────────────────────────────────────────────────────────────────────────────
# Shared LangGraph state
# ─────────────────────────────────────────────────────────────────────────────


class PipelineState(BaseModel):
    """The state object threaded through the LangGraph StateGraph (PRD §5).

    Each agent reads what it needs and writes its own output field. `steps` accumulates
    the visible reasoning; the SSE route drains it as events are produced.
    """

    # input
    question: str
    student_id: str | None = None

    # agent outputs (filled as the graph runs)
    diagnosis: Diagnosis | None = None
    strategy: Strategy | None = None
    block: ComponentBlock | None = None

    # Accumulated visible reasoning. The `operator.add` reducer makes LangGraph CONCATENATE
    # each node's returned `steps` rather than overwrite — so every node returns only the
    # steps it produced and the graph accumulates them (D-03). The metadata is inert outside
    # LangGraph (plain Pydantic list).
    steps: Annotated[list[AgentStep], operator.add] = Field(default_factory=list)


def step(agent: AgentName, status: AgentStatus, detail: str) -> AgentStep:
    """Small helper so agents can construct a step without repeating the constructor."""
    return AgentStep(agent=agent, status=status, detail=detail)
