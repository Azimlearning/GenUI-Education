# ruff: noqa: E501
'''Tests for deterministic interactive labs that do not use a model call.'''

import pytest

import graph.nodes.verifier as verifier_module
import postprocess
from graph.context import RunContext
from graph.nodes.verifier import PassedVerifierReport, verify_trusted_builtin
from services.builtin_labs import (
    HOOKES_LAW_ID,
    KOH_TITRATION_HTML,
    KOH_TITRATION_ID,
    ORBITAL_SIM_ID,
    YEAST_FERMENTATION_ID,
    is_hookes_law_brief,
    is_orbital_sim_brief,
    is_trusted_builtin_html,
    is_yeast_fermentation_products_brief,
    resolve_builtin_lab,
    resolve_builtin_lab_for_query,
)

HOOKES_QUERY = (
    'Investigate the relationship between the force applied to a spring and its extension. '
    'Materials: steel spring, slotted masses, metre ruler, retort stand and clamp.'
)

KOH_QUERY = '''Determine the concentration of potassium hydroxide solution, KOH by acid-base titration.
Materials: 1.0 mol dm-3 nitric acid, HNO3, potassium hydroxide, KOH, phenolphthalein and distilled water.
Apparatus: Burette, 25 cm3 pipette, pipette filler, 250 cm3 conical flask, white tile and retort stand.'''

YEAST_QUERY = 'What are the products of yeast fermentation?'


def test_koh_lab_matches_the_explicit_materials_and_apparatus_brief():
    lab = resolve_builtin_lab(KOH_QUERY, 'virtual_experiment', 'chemistry')
    assert lab is not None
    assert lab.key == KOH_TITRATION_ID
    assert lab.plan.interaction_mode == 'drag_drop'
    assert len(lab.plan.interaction_requirements) == 3
    for term in (
        'pointerdown', 'pointermove', 'pointerup', 'setPointerCapture',
        'releasePointerCapture', 'getBoundingClientRect', 'swirl_mix',
        'hno3_volume', 'synapse_event',
    ):
        assert term in lab.html
    assert isinstance(postprocess.forbidden_api_scan(lab.html), str)


@pytest.mark.parametrize(
    'query',
    [
        'Determine the concentration of potassium hydroxide solution, KOH by acid-base titration',
        'How do I find the concentration of KOH by titration?',
        'KOH titration experiment',
    ],
)
def test_koh_short_briefs_still_select_the_lab(query):
    lab = resolve_builtin_lab_for_query(query)
    assert lab is not None
    assert lab.key == KOH_TITRATION_ID


def test_koh_template_is_not_selected_for_a_generic_titration_curve():
    assert resolve_builtin_lab(
        'Graph the pH curve of a generic acid-base titration.',
        'virtual_experiment',
        'chemistry',
    ) is None
    # KOH mentioned but no titration task: falls through to normal generation.
    assert resolve_builtin_lab_for_query('What is the molar mass of KOH?') is None


@pytest.mark.parametrize(
    'query',
    [
        YEAST_QUERY,
        'Can you tell me what yeast fermenting glucose produces?',
        'Show a yeast fermentation experiment with limewater and paraffin oil.',
    ],
)
def test_yeast_products_questions_select_the_deterministic_experiment(query):
    assert is_yeast_fermentation_products_brief(query)
    lab = resolve_builtin_lab_for_query(query)
    assert lab is not None
    assert lab.key == YEAST_FERMENTATION_ID
    assert lab.plan.interaction_mode == 'drag_drop'
    assert lab.plan.variables[0].name == 'incubation time'


def test_yeast_matcher_does_not_hijack_unrelated_or_underspecified_questions():
    for query in (
        'What are the products of aerobic respiration?',
        'How do I bake bread with yeast?',
        'Explain yeast fermentation.',
    ):
        assert not is_yeast_fermentation_products_brief(query)


@pytest.mark.parametrize(
    'query',
    [
        HOOKES_QUERY,
        'Show how the extension of a spring changes as you add slotted masses.',
        "Demonstrate Hooke's law with a spring and hanging masses.",
    ],
)
def test_hookes_law_questions_select_the_deterministic_experiment(query):
    assert is_hookes_law_brief(query)
    lab = resolve_builtin_lab_for_query(query)
    assert lab is not None
    assert lab.key == HOOKES_LAW_ID
    assert lab.plan.interaction_mode == 'drag_drop'
    assert lab.plan.variables[0].name == 'load'


def test_hookes_matcher_does_not_hijack_unrelated_spring_questions():
    for query in (
        'How does a spring reverb pedal work in music?',
        'When does the spring season start?',
        'Explain the Spring framework for Java web apps.',
    ):
        assert not is_hookes_law_brief(query)


def test_hookes_lab_has_real_direct_manipulation_and_no_canvas_dependency():
    lab = resolve_builtin_lab(HOOKES_QUERY, 'virtual_experiment', 'physics')
    assert lab is not None
    for term in (
        'pointerdown', 'pointermove', 'pointerup', 'setPointerCapture',
        'releasePointerCapture', 'getBoundingClientRect', 'add_mass',
        'synapse_event', 'touch-action:none',
    ):
        assert term in lab.html
    assert 'createCanvas' not in lab.html
    assert '<script src=' not in lab.html
    assert isinstance(postprocess.forbidden_api_scan(lab.html), str)


async def test_hookes_builtin_mints_a_verified_report_without_an_llm(monkeypatch):
    async def emit(payload):
        pass

    lab = resolve_builtin_lab(HOOKES_QUERY, 'virtual_experiment', 'physics')
    assert lab is not None
    monkeypatch.setattr(verifier_module, 'record_trace', lambda **kwargs: None)
    outcome = verify_trusted_builtin(
        RunContext(run_id='hookes', session_id='session', emit=emit),
        lab.plan,
        lab.html,
        lab.key,
    )
    assert isinstance(outcome, PassedVerifierReport)
    assert outcome.report.verdict == 'pass'
    assert len(outcome.report.spot_checks) == 3
    assert '49' in outcome.report.spot_checks[0].expected


ORBIT_QUERY = "Simulate how a satellite's launch speed decides whether it falls back to Earth, orbits, or escapes into space."


@pytest.mark.parametrize(
    'query',
    [
        ORBIT_QUERY,
        "Show Newton's cannonball: how orbital speed shapes a satellite's path around Earth.",
        'What launch speed is needed to reach escape velocity and leave Earth?',
    ],
)
def test_orbital_sim_questions_select_the_deterministic_simulation(query):
    assert is_orbital_sim_brief(query)
    lab = resolve_builtin_lab_for_query(query)
    assert lab is not None
    assert lab.key == ORBITAL_SIM_ID
    assert lab.plan.interaction_mode == 'controls'
    assert lab.plan.variables[0].name == 'launch speed'


def test_orbital_sim_matcher_does_not_hijack_unrelated_orbit_questions():
    for query in (
        'Explain the orbitals and electron shells of a carbon atom.',
        'Describe the water cycle.',
    ):
        assert not is_orbital_sim_brief(query)


def test_orbital_sim_is_a_self_contained_canvas_with_no_vendor_dependency():
    lab = resolve_builtin_lab(ORBIT_QUERY, 'simulation', 'physics')
    assert lab is not None
    for term in ('getContext', 'requestAnimationFrame', 'synapse_ready', 'synapse_event', 'launch_speed'):
        assert term in lab.html
    assert '<script src=' not in lab.html
    assert 'createCanvas' not in lab.html
    assert isinstance(postprocess.forbidden_api_scan(lab.html), str)


async def test_orbital_sim_builtin_mints_a_verified_report_without_an_llm(monkeypatch):
    async def emit(payload):
        pass

    lab = resolve_builtin_lab(ORBIT_QUERY, 'simulation', 'earth_space')
    assert lab is not None
    monkeypatch.setattr(verifier_module, 'record_trace', lambda **kwargs: None)
    outcome = verify_trusted_builtin(
        RunContext(run_id='orbit', session_id='session', emit=emit),
        lab.plan,
        lab.html,
        lab.key,
    )
    assert isinstance(outcome, PassedVerifierReport)
    assert outcome.report.verdict == 'pass'
    assert len(outcome.report.spot_checks) == 3


def test_yeast_lab_has_real_direct_manipulation_and_no_canvas_dependency():
    lab = resolve_builtin_lab(YEAST_QUERY, 'virtual_experiment', 'biology')
    assert lab is not None
    for term in (
        'pointerdown', 'pointermove', 'pointerup', 'setPointerCapture',
        'releasePointerCapture', 'getBoundingClientRect', 'add_yeast_to_tube_a',
        'seal_tube_a', 'connect_delivery_tube_a', 'incubation_minutes',
    ):
        assert term in lab.html
    assert 'createCanvas' not in lab.html
    assert '<script src=' not in lab.html
    assert isinstance(postprocess.forbidden_api_scan(lab.html), str)


def test_only_the_exact_builtin_source_is_trusted():
    assert is_trusted_builtin_html(KOH_TITRATION_ID, KOH_TITRATION_HTML)
    assert not is_trusted_builtin_html(KOH_TITRATION_ID, KOH_TITRATION_HTML + 'x')
    yeast = resolve_builtin_lab_for_query(YEAST_QUERY)
    assert yeast is not None
    assert is_trusted_builtin_html(YEAST_FERMENTATION_ID, yeast.html)
    assert not is_trusted_builtin_html(YEAST_FERMENTATION_ID, yeast.html + 'x')


async def test_trusted_builtin_mints_a_verified_report_without_an_llm(monkeypatch):
    async def emit(payload):
        pass

    lab = resolve_builtin_lab(KOH_QUERY, 'virtual_experiment', 'chemistry')
    assert lab is not None
    monkeypatch.setattr(verifier_module, 'record_trace', lambda **kwargs: None)
    outcome = verify_trusted_builtin(
        RunContext(run_id='builtin', session_id='session', emit=emit),
        lab.plan,
        lab.html,
        lab.key,
    )
    assert isinstance(outcome, PassedVerifierReport)
    assert outcome.report.verdict == 'pass'
    assert len(outcome.report.spot_checks) == 3


async def test_yeast_builtin_mints_product_specific_verified_evidence(monkeypatch):
    async def emit(payload):
        pass

    lab = resolve_builtin_lab_for_query(YEAST_QUERY)
    assert lab is not None
    monkeypatch.setattr(verifier_module, 'record_trace', lambda **kwargs: None)
    outcome = verify_trusted_builtin(
        RunContext(run_id='yeast', session_id='session', emit=emit),
        lab.plan,
        lab.html,
        lab.key,
    )
    assert isinstance(outcome, PassedVerifierReport)
    assert 'carbon dioxide' in outcome.report.spot_checks[0].expected
    assert 'control' in outcome.report.spot_checks[1].inputs
