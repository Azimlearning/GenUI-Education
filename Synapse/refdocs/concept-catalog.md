# Synapse — Demo Concept Catalog

> **The 12 locked demo concepts (D-13)** and the interaction pattern each maps to. This is the
> build manifest for the interactive components. Mirrors `backend/app/components/registry.py`
> (`REGISTRY` + `CONCEPTS`). Update both together.

Scope decision (D-13, 2026-07-01): the team chose to attempt **all 12 concepts as real
interactives** for the demo — this supersedes the earlier "1 subject deep only" framing (D-06)
in favour of breadth across all three subjects. Risk (recorded, accepted): 12 faithful sims is a
lot for one sprint; the **build order below prioritises 3 flagships first** so there is always a
flawless fallback demo even if the long tail stays rough.

Faithfulness is still non-negotiable per built component (constraint #1) — a science-literate
judge will probe the sim. A concept is only "live" when its physics/biology is correct, not just
when it renders.

---

## Interaction patterns (the library — parameterised by pattern, not topic, D-02)

| Pattern | Subject(s) | Concepts it serves |
|---|---|---|
| `gradient-diffusion-sandbox` | Bio | Osmosis / water in plants (turgor, plasmolysis) |
| `process-timeline` | Bio | Menstrual cycle & egg movement |
| `stage-sequencer` | Bio | Cell division (mitosis / meiosis) |
| `labelled-diagram-explorer` | Bio/Chem | Digestive system (journey mode), cell/heart diagrams |
| `matching-pairs` | Bio/Chem | Enzyme↔substrate (supports digestive system) |
| `punnett-square-builder` | Bio | Genetics & inheritance |
| `signal-pathway-sim` | Bio | Neuron / nerve impulse / reflex arc |
| `reaction-lab-sandbox` | Chem | Reactions with apparatus + ingredients |
| `electron-bonding-explorer` | Chem | Bonding & electrons (ionic vs covalent chart) |
| `atomic-structure-explorer` | Chem | Atomic structure (nucleus + electron shells) |
| `force-motion-sim` | Phys | Forces & motion (ticker tape, v-t graph) |
| `circuit-builder-sandbox` | Phys | Electricity (Ohm's law, series/parallel) |
| `wave-optics-sandbox` | Phys | Waves & optics (ripple tank, ray diagrams, lenses) |
| `quick-check-quiz` | all | Retrieval practice across any topic |

---

## Build order (flagships first)

**Tier 1 — flagships (build faithful FIRST, one per subject):**
1. 🧬 **Osmosis** → `gradient-diffusion-sandbox` — the original flagship; cleanest predict-observe-explain "aha".
2. ⚗️ **Bonding & electrons** → `electron-bonding-explorer` — ionic-transfer vs covalent-share, the contrasting-cases showcase.
3. ⚙️ **Forces & motion** → `force-motion-sim` — ticker-tape trolley + linked v-t graph.

**Tier 2 — high-visual-impact:**
4. Cell division → `stage-sequencer` · 5. Circuit builder → `circuit-builder-sandbox` · 6. Atomic structure → `atomic-structure-explorer`

**Tier 3 — completes the 12:**
7. Menstrual cycle → `process-timeline` · 8. Genetics → `punnett-square-builder` · 9. Neuron → `signal-pathway-sim` · 10. Digestive system → `labelled-diagram-explorer` (+ `matching-pairs`) · 11. Waves & optics → `wave-optics-sandbox` · 12. Reactions lab → `reaction-lab-sandbox`

---

## Per-concept spec

Each: **subject · form · pattern · experiment (faithful analogue) · chatbot idea · faithfulness notes.**

### Chemistry

**C1 · Reactions in the lab** — Form 4 · `reaction-lab-sandbox`
- Experiment: interact with apparatus + ingredients → observe the reaction result.
- Chatbot: predict the product, then mix and observe; explain what happened.
- Faithful: reaction outcomes must be chemically correct (products, colour changes, gas/precipitate). Encode a small rules table, don't free-generate.

**C2 · Bonding & electrons** — Form 4 · `electron-bonding-explorer`
- Experiment: chart of substances relating electron behaviour to bond type.
- Chatbot: contrast ionic vs covalent; animate electrons transferring (ionic) vs sharing (covalent).
- Faithful: ties to misconception `bonding-sharing-vs-transfer`; electronegativity-difference rule decides bond type. Metal+non-metal → transfer; non-metal+non-metal → share.

**C3 · Atomic structure** — Form 4 · `atomic-structure-explorer`
- Experiment: build an atom — nucleus (protons/neutrons) + electron shells (Bohr model).
- Chatbot: proton/nucleon number, shell filling (2, 8, 8…), isotopes.
- Faithful: shell capacities and electron configuration must be correct for the KSSM first 20 elements.

### Physics

**P1 · Forces & motion** — Form 4 · `force-motion-sim`  *(flagship)*
- Experiment: ticker-tape trolley → velocity/acceleration; linked v-t graph.
- Chatbot: walk through v-t graphs; quiz which of Newton's laws applies.
- Faithful: motion obeys ΣF = ma; friction opposes motion; the v-t graph is derived from the sim, not faked. Ties to misconception `newton-force-needed-to-keep-moving`.

**P2 · Electricity** — Form 5 · `circuit-builder-sandbox`
- Experiment: measure voltage & current in series/parallel circuits.
- Chatbot: step-by-step Ohm's-law / circuit calculation problems.
- Faithful: V = IR; series (same current, voltages add) vs parallel (same voltage, currents add) must compute correctly.

**P3 · Waves & optics** — Form 5 · `wave-optics-sandbox`
- Experiment: ripple tank → reflection/refraction/diffraction; lenses.
- Chatbot: ray-diagram walkthroughs; wave-property Q&A.
- Faithful: refraction follows Snell's law direction; convex/concave lens ray rules correct; wavelength/frequency relationship right.

### Biology

**B1 · Menstrual cycle & egg movement** — Form 4 · `process-timeline`
- Experiment: animated 28-day cycle; egg through stages; hormone tracks (FSH, LH, oestrogen, progesterone).
- Chatbot: quiz hormone functions; "what happens on Day 14?"; predict phases.
- Faithful: ovulation ~Day 14; hormone peaks in the correct order/phase; follicle → corpus luteum.

**B2 · Osmosis & water in plants** — Form 5 · `gradient-diffusion-sandbox`  *(flagship)*
- Experiment: drag water across membranes; cells go turgid or plasmolysed.
- Chatbot: explain why plants wilt; predict cell state at a given salt concentration.
- Faithful: water moves toward higher solute (down water-potential gradient). Ties to misconception `osmosis-inverted-gradient`. `cell_mode:'plant-cell'` shows turgor/plasmolysis.

**B3 · Cell division — mitosis & meiosis** — Form 4 · `stage-sequencer`
- Experiment: drag chromosomes into correct positions per stage; animated split.
- Chatbot: "which stage is this?" quizzes; compare mitosis vs meiosis.
- Faithful: prophase → metaphase → anaphase → telophase; meiosis halves chromosome number (2 divisions), mitosis preserves it.

**B4 · Human digestive system** — Form 4 · `labelled-diagram-explorer` (+ `matching-pairs`)
- Experiment: follow a food particle through the tract; match enzyme to substrate.
- Chatbot: which enzyme breaks down starch? trace digestion of a meal.
- Faithful: amylase→starch, pepsin→protein, lipase→fat; absorption at villi in the small intestine.

**B5 · Genetics & inheritance** — Form 5 · `punnett-square-builder`
- Experiment: build a Punnett square by dragging alleles; reveal offspring probability.
- Chatbot: walk a cross ("chance of a blue-eyed child?"); genotype vs phenotype.
- Faithful: correct monohybrid (and stretch: dihybrid) ratios; dominant/recessive expression right.

**B6 · Neuron & nervous system** — Form 5 · `signal-pathway-sim`
- Experiment: animate an impulse along a neuron; trigger a reflex arc.
- Chatbot: trace a reflex action step by step; explain the synapse.
- Faithful: receptor → sensory neuron → CNS → motor neuron → effector; impulse is electrical along the axon, chemical (neurotransmitter) across the synapse.

---

## Notes carried from the UI/UX team (`../uiux_team/EDUNOVA/`)

The UI/UX team prototyped a **sidebar-chat + right visualizer-panel** layout under the working
name **"TutorLah!"**. Decision (2026-07-01): the product name stays **Synapse** and the layout
stays the **centered** `Synapse_Demo.html` shape (D-15). Salvaged from their work: the
**per-subject colour theming** (Biology green, Chemistry sand, Physics blue) — fold this into the
centered layout as a subtle subject accent once the composed component's subject is known.
