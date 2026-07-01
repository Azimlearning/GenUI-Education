# Synapse — Prompt Test Matrix

> A pressure-test checklist for the agent pipeline: what to type, and what the pipeline is
> actually *built* to produce (diagnosis → strategy → component), so a run either confirms the
> build or surfaces a real bug/gap. Grounded in `backend/app/knowledge/misconceptions.py` and
> `backend/app/components/registry.py` — not guessed. Use this before recording the demo video
> and during the subject-teacher pressure-test (see `decisions.md` P-d).
>
> Run with `ANTHROPIC_API_KEY` set in `backend/.env` for the live-Claude path. Without a key the
> pipeline falls back to the scripted `detect()` keyword matcher (D-c) — several rows below are
> flagged where the two paths diverge.

## How to read a row

Every question flows: **question → diagnosis** (`misconception` | `knowledge_gap` |
`mastery_check`) **→ strategy** (a teaching technique) **→ composed component** (a pattern +
props) **→ tutor-loop write**. "Pass criteria" is what to actually look at on screen, not just
whether it returned 200.

---

## A. Flagship happy-paths (demo + video core)

| Prompt | Expected diagnosis | Strategy | Component | Pass criteria |
|---|---|---|---|---|
| "osmosis is when water moves to where there's more water" | misconception → `osmosis-inverted-gradient` | predict-observe-explain | `gradient-diffusion-sandbox` | Predict "toward more water" → sim moves water **toward higher solute** (visible contradiction); explanation cites the water-potential gradient; tutor logs the misconception + schedules review |
| "why does a moving object need a force to keep moving?" | misconception → `newton-force-needed-to-keep-moving` | predict-observe-explain | `force-motion-sim` | Sim holds constant velocity at zero net force; friction (not "force running out") is what actually stops everyday objects; v-t graph obeys F = ma |
| "I don't understand ionic vs covalent bonding" | knowledge_gap or `bonding-sharing-vs-transfer` | contrasting cases | `electron-bonding-explorer` | Na + Cl (metal + non-metal) → electron **transfer** (ionic); contrasted against a non-metal + non-metal pair → electron **share** (covalent) |

## B. Other misconceptions in the KB

| Prompt | Expected | Watch for |
|---|---|---|
| "current gets used up as it goes round the circuit" | misconception → `current-used-up` → `circuit-builder-sandbox` | ⚠ Confirm the sim shows an **equal ammeter reading** on both sides of a bulb (charge conserved, energy transferred — not current disappearing). Pressure-test this one specifically. |
| "plants get their food from the soil through their roots" | misconception → `photosynthesis-food-from-soil` → *(no pattern currently serves this topic)* | 🔴 **Known gap:** no `ComponentPattern.serves_topics` lists "photosynthesis" in the registry, so `find_pattern_for("photosynthesis")` returns `None`. The Composer will mismatch or fall back. Either fix the registry (add "photosynthesis" to a pattern's `serves_topics`, e.g. `gradient-diffusion-sandbox` for gas exchange, or a dedicated pattern) or drop this prompt from the demo until fixed. |

## C. Knowledge-gap prompts (genuine "teach me", no misconception)

| Prompt | Expected component |
|---|---|
| "explain the menstrual cycle" | `process-timeline` |
| "how does a neuron carry a signal?" | `signal-pathway-sim` |
| "what's the difference between proton number and nucleon number?" | `atomic-structure-explorer` |
| "how do I balance H2 + O2 → H2O?" | `quick-check-quiz` (coefficients) |
| "chance of a blue-eyed child from Bb × Bb?" | `punnett-square-builder` |
| "trace food through the digestive system" | `labelled-diagram-explorer` (journey mode) |

## D. Adversarial / seam-stress

These are the ones most likely to expose a real bug rather than confirm a happy path.

| Prompt | Why it's a test | Expected |
|---|---|---|
| Re-ask osmosis *after clearing it* (same `student_id`) | P3 history-awareness | Diagnosis flips to **`mastery_check`**, not re-teaching the same misconception |
| "osmosis is water moving from low to high solute across a membrane" (this is *correct*) | Does the Diagnostician over-diagnose a misconception that isn't there? | Should resolve to `mastery_check` or a plain knowledge confirmation — must NOT be forced into `osmosis-inverted-gradient` |
| "there's more water in the river after rain" | Keyword-trigger over-fire | Live LLM path should not flag osmosis. The **scripted fallback WILL falsely match** (`detect()` triggers on the substring `"more water"`) — good side-by-side demo of live-Claude vs scripted quality |
| "explain quantum entanglement" (off-syllabus) | Graceful failure | Honest scope limit / knowledge_gap fallback — no crash, no hallucinated or mismatched sim |

## E. Known divergence: scripted fallback vs live Claude

The no-key scripted `detect()` matcher in `misconceptions.py` uses broad substring triggers
(`"osmos"`, `"more water"`, `"ionic"`, `"covalent"`, `"bond"`, `"keep moving"`, `"current used
up"`, `"used up"`, `"from the soil"`, `"food from"`). These over-fire easily. Worth demonstrating
deliberately:

1. Run a borderline prompt (e.g. row D3) with **no API key** → scripted fallback likely
   misfires.
2. Run the same prompt **with `ANTHROPIC_API_KEY` set** → live Claude classifies correctly.

This contrast is a legitimate "why grounded LLM diagnosis beats keyword matching" beat if you
want it in the video, not just a bug to hide.

## Running the suite

Manual: type each prompt into the landing page, one at a time, and check the pass criteria
against what streams in on screen (agent trace + composed interactive + tutor-loop log line).

Scripted: `POST /api/ask` with `{"question": "...", "student_id": "prompt-test"}` and read the
`component_block` event's `pattern` + the diagnostician's `agent_step` detail — see
`backend/app/api/routes.py` for the exact SSE event shapes.
