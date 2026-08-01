"""Router output schema. Anchored in docs/DATA_MODEL.md (pydantic schema anchors)."""

from typing import Literal

from pydantic import BaseModel, Field

ArtifactType = Literal[
    "simulation",
    "explorable_diagram",
    "virtual_experiment",
    "data_visualization",
    "text_only",
]
Domain = Literal["physics", "chemistry", "biology", "earth_space", "math_adjacent"]


class Intent(BaseModel):
    """Full Router classification, including the cache-key concept label."""

    artifact_type: ArtifactType
    domain: Domain
    complexity: Literal[1, 2, 3]
    canonical_concept: str = Field(
        min_length=1,
        max_length=120,
        pattern=r"^[a-z0-9]+(_[a-z0-9]+)*$",
        description="snake_case, singular, qualifier-ordered concept label",
    )

    @property
    def public(self) -> "IntentPublic":
        return IntentPublic(
            artifact_type=self.artifact_type,
            domain=self.domain,
            complexity=self.complexity,
        )


class IntentPublic(BaseModel):
    """Intent as exposed in the SSE `meta` event (API_SPEC.md section 2)."""

    artifact_type: ArtifactType
    domain: Domain
    complexity: Literal[1, 2, 3]
