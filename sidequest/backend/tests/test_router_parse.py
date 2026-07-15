import pytest
from pydantic import ValidationError

from graph.nodes.router import parse_intent

CLEAN = (
    '{"artifact_type": "simulation", "domain": "physics", '
    '"complexity": 2, "canonical_concept": "projectile_motion"}'
)


def test_parses_clean_json():
    assert parse_intent(CLEAN).canonical_concept == "projectile_motion"


def test_parses_fenced_json():
    assert parse_intent(f"```json\n{CLEAN}\n```").domain == "physics"


def test_parses_json_with_surrounding_prose():
    assert parse_intent(f"Here is the classification:\n{CLEAN}\nDone.").complexity == 2


def test_rejects_garbage():
    with pytest.raises(ValueError):
        parse_intent("no json here at all")


def test_rejects_wrong_enum():
    with pytest.raises(ValidationError):
        parse_intent(CLEAN.replace("simulation", "hologram"))
