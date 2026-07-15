import pytest
from pydantic import ValidationError

from schemas.intent import Intent


def test_valid_intent():
    intent = Intent(
        artifact_type="virtual_experiment",
        domain="chemistry",
        complexity=3,
        canonical_concept="acid_base_titration",
    )
    assert intent.public.artifact_type == "virtual_experiment"


@pytest.mark.parametrize(
    "concept",
    ["Has_Upper", "has space", "trailing_", "_leading", "double__underscore", ""],
)
def test_canonical_concept_must_be_snake_case(concept):
    with pytest.raises(ValidationError):
        Intent(
            artifact_type="simulation",
            domain="physics",
            complexity=1,
            canonical_concept=concept,
        )


def test_complexity_is_bounded():
    with pytest.raises(ValidationError):
        Intent(
            artifact_type="simulation",
            domain="physics",
            complexity=4,
            canonical_concept="ok_concept",
        )
