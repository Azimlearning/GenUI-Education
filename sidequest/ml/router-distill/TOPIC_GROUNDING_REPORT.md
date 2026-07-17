# KSSM topic-grounding report

Status: review only. This report does **not** modify `kssm_topics.py`.

Date: 2026-07-17

## Evidence and method

The six supplied DLP textbooks in `ml/rag/sources/` were inspected directly
with `pypdf`. Chapter titles below come from their contents pages, not from
model-generated topic labels:

| Subject/form | Source file | Contents PDF page(s) |
|---|---|---:|
| Biology F4 | `[DLP] BIOLOGY F4.pdf` | 4-5 |
| Biology F5 | `[DLP] BIOLOGY FORM 5.pdf` | 4-6 |
| Chemistry F4 | `CHEMISTRY F4.pdf` | 5-6 |
| Chemistry F5 | `CHEMISTRY F5.pdf` | 5 |
| Physics F4 | `PHYSICS F4_removed.pdf` | 2-3 |
| Physics F5 | `PHYSICS F5_removed.pdf` | 4-5 |

`kssm_topics.py` currently has 40 hand-drafted labels. The textbook chapter
structure has 54 chapter-level topics (Biology 15 + 13, Chemistry 8 + 5,
Physics 6 + 7). The recommendation is to make one reviewed generator topic
per textbook chapter unless a human deliberately approves a narrower scope.

## Findings by subject and form

### Biology Form 4

Current matches: cell structure/organisation (Chapter 2), movement across the
plasma membrane (3), chemical composition in a cell (4), cell division (6),
cellular respiration (7), and nutrition/human digestive system (9).

Corrections required:

- `respiration` conflates **Chapter 7 Cellular Respiration** with **Chapter 8
  Respiratory Systems in Humans and Animals**. Split them.
- `dynamic_ecosystem` and `endangered_ecosystem` have no Form 4 chapter match;
  they belong with the Form 5 ecosystem/environment material.

Missing textbook chapters: Introduction to Biology and Laboratory Rules (1),
Metabolism and Enzymes (5), Transport in Humans and Animals (10), Immunity in
Humans (11), Coordination and Response in Humans (12), Homeostasis and the
Human Urinary System (13), Support and Movement in Humans and Animals (14),
and Sexual Reproduction, Development and Growth in Humans and Animals (15).

### Biology Form 5

Current matches: Inheritance (11), Genetic Technology (13, currently called
`molecular_genetics`), and Environmental Sustainability (10, currently called
`human_impact_on_ecosystem`).

Corrections required:

- `support_and_movement`, `coordination_and_response`, and the current
  human-focused `reproduction_and_growth` are Form 4 topics, not Form 5.
- `evolution` has no chapter-level match in the supplied Form 5 textbook.

Missing textbook chapters: Organisation of Plant Tissues and Growth (1), Leaf
Structure and Function (2), Nutrition in Plants (3), Transport in Plants (4),
Response in Plants (5), Sexual Reproduction in Flowering Plants (6),
Adaptations of Plants in Different Habitats (7), Biodiversity (8), Ecosystem
(9), and Variation (12).

### Chemistry Form 4

Current matches: Matter/atomic structure (2), the mole concept/chemical
formula/equation (3), Periodic Table of Elements (4), Chemical Bond (5), and
Acid, Base and Salt (6).

Corrections required:

- `periodic_table` is misnamed: its label and hint describe Chapter 3, while
  the slug implies Chapter 4. Use distinct topics for the Mole Concept,
  Chemical Formula and Equation (3) and Periodic Table of Elements (4).
- `electrochemistry` has no Form 4 chapter-level match.

Missing textbook chapters: Introduction to Chemistry (1), Rate of Reaction
(7), and Manufactured Substances in Industry (8).

### Chemistry Form 5

Current matches: Redox Equilibrium (1), Carbon Compounds (2), Thermochemistry
(3), and Consumer and Industrial Chemistry (5).

Corrections required:

- `rate_of_reaction` and `manufactured_substances_in_industry` are Form 4
  topics, not Form 5.

Missing textbook chapter: Polymer (4).

### Physics Form 4

Current matches: Measurement (1), Force and Motion I (2; the current split
between kinematics and momentum is supportable as subtopics), and Heat (4).

Corrections required:

- `forces_and_pressure` is a Form 5 topic (Chapter 2 Pressure).
- `elasticity` is a Form 5 topic (Chapter 1 Force and Motion II).

Missing textbook chapters: Gravitation (3), Waves (5), and Light and Optics
(6).

### Physics Form 5


## Proposed source taxonomy (approval target)

This is the complete chapter-level inventory proposed for generation after
review. It intentionally uses textbook titles before slug naming is decided.

| Subject/form | Proposed reviewed topics, in textbook order |
|---|---|
| Biology F4 | Introduction to Biology and Laboratory Rules; Cell Biology and Organisation; Movement of Substances across a Plasma Membrane; Chemical Composition in a Cell; Metabolism and Enzymes; Cell Division; Cellular Respiration; Respiratory Systems in Humans and Animals; Nutrition and the Human Digestive System; Transport in Humans and Animals; Immunity in Humans; Coordination and Response in Humans; Homeostasis and the Human Urinary System; Support and Movement in Humans and Animals; Sexual Reproduction, Development and Growth in Humans and Animals |
| Biology F5 | Organisation of Plant Tissues and Growth; Leaf Structure and Function; Nutrition in Plants; Transport in Plants; Response in Plants; Sexual Reproduction in Flowering Plants; Adaptations of Plants in Different Habitats; Biodiversity; Ecosystem; Environmental Sustainability; Inheritance; Variation; Genetic Technology |
| Chemistry F4 | Introduction to Chemistry; Matter and the Atomic Structure; The Mole Concept, Chemical Formula and Equation; The Periodic Table of Elements; Chemical Bond; Acid, Base and Salt; Rate of Reaction; Manufactured Substances in Industry |
| Chemistry F5 | Redox Equilibrium; Carbon Compounds; Thermochemistry; Polymer; Consumer and Industrial Chemistry |
| Physics F4 | Measurement; Force and Motion I; Gravitation; Heat; Waves; Light and Optics |
| Physics F5 | Force and Motion II; Pressure; Electricity; Electromagnetism; Electronics; Nuclear Physics; Quantum Physics |
Current matches: Electricity (3), Electromagnetism (4), Electronics (5), and
Nuclear Physics (6).

Corrections required:

- `waves` and `light_and_optics` are Form 4 topics, not Form 5.

Missing textbook chapters: Force and Motion II (1), Pressure (2), and Quantum
Physics (7).

## Experiment-placement check

The two standalone biology write-ups are correctly placed in `biology/form4/`:

- `5.1 Effect of temperature on amylase activity.pdf` identifies itself as
  **Activity 5.1**, studying amylase enzyme activity. The Form 4 contents
  place the relevant work in Chapter 5 *Metabolism and Enzymes* (the wording
  aligns most closely with section 5.2 Enzymes, despite the activity number).
- `7.3 Studying yeast fermentation.pdf` identifies itself as **Activity 7.3**;
  the Form 4 contents list section 7.3 *Fermentation* exactly.

## Required human decision before editing the taxonomy

Approve or amend the proposed chapter-level scope and the form moves above.
After approval, update `kssm_topics.py` with one source comment per
subject/form and retain this report as its review record. Do not use the
current taxonomy for grounded regeneration until that review is complete.
