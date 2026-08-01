import pytest
from pydantic import ValidationError

from graph.nodes.router import parse_intent, promote_builtin_lab, promote_process_lookup
from schemas.intent import Intent

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


def test_lowercases_scientific_notation_in_canonical_concept():
    # Live finding (2026-07-18): the model reaches for "pH" even when told
    # snake_case, which broke the lowercase-only regex and risked a silent
    # misroute to text_only. Lowercasing in parse_intent fixes it.
    raw = CLEAN.replace("projectile_motion", "acid_base_titration_pH_change")
    assert parse_intent(raw).canonical_concept == "acid_base_titration_ph_change"


def test_process_product_lookup_promotes_to_explorable_diagram():
    intent = Intent(
        artifact_type="text_only",
        domain="chemistry",
        complexity=1,
        canonical_concept="yeast_fermentation_products",
    )
    promoted = promote_process_lookup("What are the products of yeast fermentation?", intent)
    assert promoted.artifact_type == "explorable_diagram"
    assert promoted.complexity == 2


def test_atomic_lookup_remains_text_only():
    intent = Intent(
        artifact_type="text_only",
        domain="chemistry",
        complexity=1,
        canonical_concept="boiling_point_water",
    )
    assert promote_process_lookup("What is the boiling point of water?", intent) == intent


def test_explicit_koh_titration_brief_forces_the_builtin_lab_route():
    intent = Intent(
        artifact_type='text_only',
        domain='math_adjacent',
        complexity=1,
        canonical_concept='unclassified_query',
    )
    routed = promote_builtin_lab(
        'Determine KOH by titration. Materials: HNO3 and KOH. Apparatus: '
        'burette, pipette and conical flask.',
        intent,
    )
    assert routed.artifact_type == 'virtual_experiment'
    assert routed.domain == 'chemistry'
    assert routed.canonical_concept == 'koh_titration_unknown_concentration'


def test_yeast_products_question_forces_the_builtin_biology_lab_route():
    intent = Intent(
        artifact_type='text_only',
        domain='math_adjacent',
        complexity=1,
        canonical_concept='unclassified_query',
    )
    routed = promote_builtin_lab('What are the products of yeast fermentation?', intent)
    assert routed.artifact_type == 'virtual_experiment'
    assert routed.domain == 'biology'
    assert routed.complexity == 3
    assert routed.canonical_concept == 'yeast_fermentation_products'
