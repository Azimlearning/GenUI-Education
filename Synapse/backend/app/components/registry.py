"""Component registry + demo concept catalog (PRD §6, concept-catalog.md).

Two data tables:
  - REGISTRY: interaction PATTERNS (D-02). One React component per pattern; topics are
    configurations of a pattern. The Composer selects a pattern and configures its props.
  - CONCEPTS: the 12 demo concepts the team locked (D-13), each pinned to a primary pattern
    plus its faithful experiment + chatbot idea. This is the build manifest for the one-shot.

`prop_schema` documents the props the matching React component expects (name → description),
kept lightweight in P0; promote load-bearing ones to Pydantic models as components are built.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import Technique


@dataclass(frozen=True)
class ComponentPattern:
    pattern: str  # id shared with the frontend library (frontend/lib/blocks.ts)
    title: str
    subjects: list[str]  # Biology / Chemistry / Physics
    serves_topics: list[str]  # example topics this pattern can be configured for
    techniques: list[Technique]  # pedagogical moves this pattern supports well
    prop_schema: dict[str, str] = field(default_factory=dict)  # prop name → description
    status: str = "planned"  # "live" (faithful) | "placeholder" | "planned"


REGISTRY: dict[str, ComponentPattern] = {
    # ── Biology ──────────────────────────────────────────────────────────────
    "gradient-diffusion-sandbox": ComponentPattern(
        pattern="gradient-diffusion-sandbox",
        title="Gradient / diffusion sandbox",
        subjects=["Biology"],
        serves_topics=["osmosis", "diffusion", "dialysis", "gas exchange", "active transport",
                       "turgor", "plasmolysis"],
        techniques=[Technique.predict_observe_explain, Technique.contrasting_cases],
        prop_schema={
            "particle": "the diffusing species label, e.g. 'water' | 'solute'",
            "left_concentration": "0-100 solute concentration on the left compartment",
            "right_concentration": "0-100 solute concentration on the right compartment",
            "membrane": "'selectively-permeable' | 'permeable' | 'impermeable'",
            "predict_prompt": "the prediction question posed before running",
            "correct_direction": "'toward-higher-solute' — the faithful answer to reveal",
            "cell_mode": "optional: 'plant-cell' to show turgor/plasmolysis instead of a beaker",
        },
        status="placeholder",  # flagship — becomes 'live' first
    ),
    "process-timeline": ComponentPattern(
        pattern="process-timeline",
        title="Animated process timeline",
        subjects=["Biology"],
        serves_topics=["menstrual cycle", "egg movement", "hormonal cycle", "cardiac cycle"],
        techniques=[Technique.predict_observe_explain, Technique.retrieval_practice],
        prop_schema={
            "duration_label": "e.g. '28-day cycle'",
            "stages": "ordered [{ day/label, title, blurb, markers }]",
            "tracks": "optional overlaid series, e.g. hormone levels (FSH, LH, oestrogen)",
            "quiz_points": "optional 'what happens on Day 14?' checkpoints",
        },
    ),
    "stage-sequencer": ComponentPattern(
        pattern="stage-sequencer",
        title="Drag-into-stage sequencer",
        subjects=["Biology"],
        serves_topics=["mitosis", "meiosis", "cell division", "protein synthesis stages"],
        techniques=[Technique.contrasting_cases, Technique.retrieval_practice],
        prop_schema={
            "stages": "ordered stage names (prophase → telophase)",
            "tokens": "draggable items (chromosomes) with correct target stage",
            "compare": "optional second process to contrast side-by-side (mitosis vs meiosis)",
        },
    ),
    "labelled-diagram-explorer": ComponentPattern(
        pattern="labelled-diagram-explorer",
        title="Labelled diagram explorer",
        subjects=["Biology", "Chemistry"],
        serves_topics=["animal cell", "plant cell", "heart", "digestive system", "villi",
                       "electrolytic cell"],
        techniques=[Technique.labelled_exploration, Technique.retrieval_practice],
        prop_schema={
            "diagram": "diagram id, e.g. 'animal-cell' | 'digestive-tract'",
            "parts": "list of { id, label, blurb } hotspots",
            "mode": "'explore' | 'label-quiz' | 'journey' (follow a particle through the tract)",
        },
    ),
    "matching-pairs": ComponentPattern(
        pattern="matching-pairs",
        title="Matching pairs",
        subjects=["Biology", "Chemistry"],
        serves_topics=["enzyme-substrate", "organ-function", "ion-charge"],
        techniques=[Technique.retrieval_practice],
        prop_schema={
            "left": "items to match from (e.g. enzymes: amylase, pepsin, lipase)",
            "right": "items to match to (e.g. substrates: starch, protein, fat)",
            "correct": "the correct pairing map",
        },
    ),
    "punnett-square-builder": ComponentPattern(
        pattern="punnett-square-builder",
        title="Punnett square builder",
        subjects=["Biology"],
        serves_topics=["genetics", "inheritance", "monohybrid cross", "dihybrid cross"],
        techniques=[Technique.predict_observe_explain, Technique.worked_example_fading],
        prop_schema={
            "parent1": "alleles, e.g. 'Bb'",
            "parent2": "alleles, e.g. 'Bb'",
            "trait": "phenotype mapping, e.g. { 'B': 'brown eyes', 'b': 'blue eyes' }",
            "cross_type": "'monohybrid' | 'dihybrid'",
        },
    ),
    "signal-pathway-sim": ComponentPattern(
        pattern="signal-pathway-sim",
        title="Signal pathway simulator",
        subjects=["Biology"],
        serves_topics=["neuron", "nerve impulse", "synapse", "reflex arc"],
        techniques=[Technique.predict_observe_explain, Technique.labelled_exploration],
        prop_schema={
            "pathway": "ordered nodes (receptor → sensory neuron → CNS → motor neuron → effector)",
            "animate": "trigger an impulse animation along the pathway",
            "synapse_detail": "optional zoom-in on neurotransmitter crossing the synapse",
        },
    ),
    # ── Chemistry ────────────────────────────────────────────────────────────
    "reaction-lab-sandbox": ComponentPattern(
        pattern="reaction-lab-sandbox",
        title="Reaction lab sandbox",
        subjects=["Chemistry"],
        serves_topics=["reactions", "apparatus", "acids and bases", "salts", "electrolysis"],
        techniques=[Technique.predict_observe_explain],
        prop_schema={
            "apparatus": "selectable apparatus (test tube, beaker, burette, electrodes)",
            "reagents": "draggable ingredients with correct reaction outcomes",
            "reaction_rules": "which reagent combos produce which observable result",
            "predict_prompt": "the prediction question before mixing",
        },
    ),
    "electron-bonding-explorer": ComponentPattern(
        pattern="electron-bonding-explorer",
        title="Electron & bonding explorer",
        subjects=["Chemistry"],
        serves_topics=["chemical bonding", "ionic vs covalent", "electron configuration",
                       "valence electrons"],
        techniques=[Technique.contrasting_cases, Technique.labelled_exploration],
        prop_schema={
            "elements": "the atoms in play with their electron configuration",
            "mode": "'transfer' (ionic) | 'share' (covalent) — animate electron behaviour",
            "chart": "periodic-context chart relating electronegativity → bond type",
        },
    ),
    "atomic-structure-explorer": ComponentPattern(
        pattern="atomic-structure-explorer",
        title="Atomic structure explorer",
        subjects=["Chemistry"],
        serves_topics=["atomic structure", "nucleus", "electron shells", "isotopes",
                       "proton number", "nucleon number"],
        techniques=[Technique.labelled_exploration, Technique.predict_observe_explain],
        prop_schema={
            "protons": "count",
            "neutrons": "count",
            "shells": "electron count per shell (2, 8, 8, …)",
            "show": "'bohr-model' | 'shell-diagram'",
        },
    ),
    # ── Physics ──────────────────────────────────────────────────────────────
    "force-motion-sim": ComponentPattern(
        pattern="force-motion-sim",
        title="Force & motion sandbox",
        subjects=["Physics"],
        serves_topics=["Newton's first law", "Newton's second law", "momentum", "friction",
                       "velocity", "acceleration", "ticker tape"],
        techniques=[Technique.predict_observe_explain],
        prop_schema={
            "mass": "kg",
            "applied_force": "N",
            "friction": "coefficient, 0-1",
            "predict_prompt": "the prediction question",
            "show_graph": "'v-t' | 'a-t' | none — linked motion graph (ticker-tape analogue)",
        },
    ),
    "circuit-builder-sandbox": ComponentPattern(
        pattern="circuit-builder-sandbox",
        title="Circuit builder sandbox",
        subjects=["Physics"],
        serves_topics=["electricity", "Ohm's law", "series circuit", "parallel circuit", "power",
                       "voltage", "current", "resistance", "safety features"],
        techniques=[Technique.predict_observe_explain, Technique.worked_example_fading],
        prop_schema={
            "components": "cells, resistors, bulbs, switches, ammeter, voltmeter",
            "topology": "'series' | 'parallel' | 'freeform'",
            "predict_prompt": "e.g. 'what does the ammeter read?'",
            "show_calculation": "step-by-step Ohm's-law working",
        },
    ),
    "wave-optics-sandbox": ComponentPattern(
        pattern="wave-optics-sandbox",
        title="Waves & optics sandbox",
        subjects=["Physics"],
        serves_topics=["wave properties", "reflection", "refraction", "diffraction", "lenses",
                       "ripple tank", "ray diagrams"],
        techniques=[Technique.predict_observe_explain, Technique.labelled_exploration],
        prop_schema={
            "mode": "'ripple-tank' | 'ray-diagram' | 'lens'",
            "wavelength": "for ripple/diffraction",
            "medium_change": "for refraction (n1 → n2)",
            "lens": "for optics: 'convex' | 'concave', focal length, object distance",
        },
    ),
    # ── Cross-subject retrieval ────────────────────────────────────────────────
    "quick-check-quiz": ComponentPattern(
        pattern="quick-check-quiz",
        title="Quick-check quiz",
        subjects=["Biology", "Chemistry", "Physics"],
        serves_topics=["balancing equations", "unit checks", "formula recall", "any retrieval"],
        techniques=[Technique.retrieval_practice],
        prop_schema={
            "prompt": "the question stem, e.g. 'Balance: H2 + O2 -> H2O'",
            "answer_type": "'coefficients' | 'mcq' | 'numeric'",
            "options": "for mcq: the choices",
            "correct": "the correct answer, checked client-side for instant feedback",
        },
    ),
    # `titration-sandbox` folded into `reaction-lab-sandbox` (D-13) — kept as an alias topic there.
}


# ─────────────────────────────────────────────────────────────────────────────
# Demo concept catalog (D-13) — the 12 locked concepts. See refdocs/concept-catalog.md.
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Concept:
    id: str
    subject: str
    form: int
    title: str
    topic: str  # aligns with a pattern's serves_topics + the misconception KB
    pattern: str  # primary interaction pattern (key into REGISTRY)
    experiment: str  # the faithful hands-on analogue
    chatbot_idea: str  # how the agent/chat can drive it
    secondary_patterns: list[str] = field(default_factory=list)


CONCEPTS: dict[str, Concept] = {
    # Chemistry
    "chem-reaction-lab": Concept(
        id="chem-reaction-lab", subject="Chemistry", form=4, title="Reactions in the lab",
        topic="reactions", pattern="reaction-lab-sandbox",
        experiment="Interact with apparatus + ingredients to see the reaction result.",
        chatbot_idea="Predict the product, then mix and observe; explain what happened.",
    ),
    "chem-bonding-electrons": Concept(
        id="chem-bonding-electrons", subject="Chemistry", form=4, title="Bonding & electrons",
        topic="chemical bonding", pattern="electron-bonding-explorer",
        experiment="Chart of substances relating electron behaviour to bond type.",
        chatbot_idea="Contrast ionic vs covalent; watch electrons transfer vs share.",
    ),
    "chem-atomic-structure": Concept(
        id="chem-atomic-structure", subject="Chemistry", form=4, title="Atomic structure",
        topic="atomic structure", pattern="atomic-structure-explorer",
        experiment="Build an atom: nucleus (protons/neutrons) + electron shells.",
        chatbot_idea="Ask about proton/nucleon number, shells, isotopes.",
    ),
    # Physics
    "phys-forces-motion": Concept(
        id="phys-forces-motion", subject="Physics", form=4, title="Forces & motion",
        topic="Newton's first law", pattern="force-motion-sim",
        experiment="Ticker-tape trolley → velocity/acceleration.",
        chatbot_idea="Walk through v-t graphs; quiz which of Newton's laws applies.",
    ),
    "phys-electricity": Concept(
        id="phys-electricity", subject="Physics", form=5, title="Electricity",
        topic="Ohm's law", pattern="circuit-builder-sandbox",
        experiment="Measure voltage & current in series/parallel circuits.",
        chatbot_idea="Step-by-step circuit calculation problems.",
    ),
    "phys-waves-optics": Concept(
        id="phys-waves-optics", subject="Physics", form=5, title="Waves & optics",
        topic="wave properties", pattern="wave-optics-sandbox",
        experiment="Ripple tank → reflection/refraction/diffraction; lenses.",
        chatbot_idea="Ray-diagram walkthroughs; Doppler / wave-property Q&A.",
    ),
    # Biology
    "bio-menstrual-cycle": Concept(
        id="bio-menstrual-cycle", subject="Biology", form=4, title="Menstrual cycle & egg movement",
        topic="menstrual cycle", pattern="process-timeline",
        experiment="Animated 28-day cycle; egg moving through stages; hormone tracks.",
        chatbot_idea="Quiz hormone functions; 'what happens on Day 14?'; predict phases.",
    ),
    "bio-osmosis-plants": Concept(
        id="bio-osmosis-plants", subject="Biology", form=5, title="Osmosis & water in plants",
        topic="osmosis", pattern="gradient-diffusion-sandbox",
        experiment="Drag water across membranes; cells go turgid or plasmolysed.",
        chatbot_idea="Explain why plants wilt; predict cell state at a salt concentration.",
    ),
    "bio-cell-division": Concept(
        id="bio-cell-division", subject="Biology", form=4, title="Cell division — mitosis & meiosis",
        topic="mitosis", pattern="stage-sequencer",
        experiment="Drag chromosomes into correct positions per stage; animated split.",
        chatbot_idea="'Which stage is this?' quizzes; compare mitosis vs meiosis.",
    ),
    "bio-digestive-system": Concept(
        id="bio-digestive-system", subject="Biology", form=4, title="Human digestive system",
        topic="digestive system", pattern="labelled-diagram-explorer",
        experiment="Follow a food particle through the tract; match enzyme to substrate.",
        chatbot_idea="Which enzyme breaks down starch? Trace digestion of a meal.",
        secondary_patterns=["matching-pairs"],
    ),
    "bio-genetics": Concept(
        id="bio-genetics", subject="Biology", form=5, title="Genetics & inheritance",
        topic="genetics", pattern="punnett-square-builder",
        experiment="Build a Punnett square by dragging alleles; reveal probabilities.",
        chatbot_idea="Walk a cross ('chance of a blue-eyed child?'); genotype vs phenotype.",
    ),
    "bio-neuron": Concept(
        id="bio-neuron", subject="Biology", form=5, title="Neuron & nervous system",
        topic="neuron", pattern="signal-pathway-sim",
        experiment="Animate an impulse along a neuron; trigger a reflex arc.",
        chatbot_idea="Trace a reflex action step by step; explain the synapse.",
    ),
}


def get_pattern(pattern: str) -> ComponentPattern | None:
    return REGISTRY.get(pattern)


def get_concept(concept_id: str) -> Concept | None:
    return CONCEPTS.get(concept_id)


def concepts_for_subject(subject: str) -> list[Concept]:
    return [c for c in CONCEPTS.values() if c.subject.lower() == subject.lower()]


def find_pattern_for(topic: str, technique: Technique | None = None) -> ComponentPattern | None:
    """Best-effort lookup used by the Composer: match on topic, optionally filter by technique."""
    topic_l = topic.lower()
    candidates = [
        p
        for p in REGISTRY.values()
        if any(topic_l in t.lower() or t.lower() in topic_l for t in p.serves_topics)
    ]
    if technique is not None:
        preferred = [p for p in candidates if technique in p.techniques]
        if preferred:
            return preferred[0]
    return candidates[0] if candidates else None
