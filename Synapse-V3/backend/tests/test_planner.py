'''Planner policy tests that do not make live model calls.'''

from graph.nodes.planner import (
    enforce_explicit_titration_drag,
    enforce_virtual_experiment_interactions,
)
from schemas.plan import ArtifactPlan, Variable


def controls_plan() -> ArtifactPlan:
    return ArtifactPlan(
        title='KOH Titration Lab',
        learning_objective='Find an unknown KOH concentration.',
        variables=[Variable(name='acid volume', unit='cm3', min=0, max=50, default=0)],
        governing_model='n(HNO3) = n(KOH) at a 1:1 endpoint.',
        expected_behaviors=['endpoint volume determines KOH concentration'],
        layout_notes='Show a flask and a burette with controls beside them.',
        library='none',
        interaction_mode='controls',
        study_note='At the endpoint, acid and base moles are equal.',
        steps=['Add acid.', 'Record the endpoint.'],
    )


def test_explicit_titration_apparatus_forces_one_drag_transfer():
    plan = enforce_explicit_titration_drag(
        controls_plan(),
        'Determine KOH by titration. Materials: HNO3 and KOH. Apparatus: '
        'burette, 25 cm3 pipette, conical flask and indicator.',
        'virtual_experiment',
    )
    assert plan.interaction_mode == 'drag_drop'
    assert '25 cm3 KOH pipette' in plan.layout_notes
    assert 'conical flask' in plan.layout_notes
    assert len(plan.steps) == 3
    assert plan.steps[0].startswith('Drag the 25 cm3 KOH pipette')
    assert 'exactly one' in plan.layout_notes
    assert len(plan.interaction_requirements) == 3
    assert 'Swirl' in plan.interaction_requirements[1]


def test_abstract_titration_without_apparatus_can_remain_controls():
    plan = controls_plan()
    assert (
        enforce_explicit_titration_drag(
            plan, 'Graph the pH curve of a generic acid-base titration.', 'virtual_experiment'
        )
        == plan
    )


def test_virtual_experiment_gets_two_direct_interaction_requirements():
    plan = enforce_virtual_experiment_interactions(controls_plan(), 'virtual_experiment')
    assert len(plan.interaction_requirements) == 2
    assert 'direct-manipulation' in plan.interaction_requirements[0]
