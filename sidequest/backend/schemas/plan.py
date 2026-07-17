"""ArtifactPlan: the Planner's output and the contract the Verifier checks
against. Anchored in docs/DATA_MODEL.md (pydantic schema anchors).

Field length caps bound free-text smuggling through the plan (SECURITY.md
section 5: the Generator sees the plan, never raw user text).
"""

from typing import Literal

from pydantic import BaseModel, Field

Library = Literal["p5", "matter", "three", "chart", "d3", "none"]
InteractionMode = Literal["controls", "drag_drop"]


class Variable(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    unit: str = Field(max_length=32)  # empty string for dimensionless
    min: float
    max: float
    default: float


class ArtifactPlan(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    learning_objective: str = Field(min_length=1, max_length=400)
    variables: list[Variable] = Field(min_length=1, max_length=3)
    governing_model: str = Field(
        min_length=1,
        max_length=4000,
        description="Explicit equations/mechanism text, e.g. y(t) = v0*sin(theta)*t - 0.5*g*t^2",
    )
    expected_behaviors: list[str] = Field(
        min_length=1, max_length=8, description="Qualitative assertions the Verifier checks"
    )
    layout_notes: str = Field(max_length=1200)
    library: Library
    interaction_mode: InteractionMode = "controls"
    # The learner-facing note and (for experiments) procedure the Generator
    # renders INSIDE the artifact itself, not left to the chat transcript
    # (UX_IMPROVEMENT_PLAN.md W3: "note inside the artifact, not chat text").
    study_note: str = Field(
        min_length=1,
        max_length=400,
        description="2-3 sentence scannable takeaway, rendered as a card inside the artifact",
    )
    steps: list[str] = Field(
        default_factory=list,
        max_length=6,
        description="Numbered procedure steps; required for virtual_experiment / drag_drop, "
        "empty otherwise",
    )
