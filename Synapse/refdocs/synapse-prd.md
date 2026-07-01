# Synapse — Product Requirements Document

> **Source of truth.** Owns scope, the four agents, the component library, architecture, provider strategy, roadmap, and the Decision Log. The short operating brief is `CLAUDE.md`; current build state is `refdocs/STATUS.md`.
> Last updated: 2026-07-01 · Team Dang Wangi (UTP)

---

## 1. One-liner

> **Google generates a UI for a topic. Synapse orchestrates a team of pedagogical agents that diagnose a student and *compose* the right interactive learning experience — and you can watch them do it.**

Synapse is an adaptive, agentic science-learning platform for Malaysian secondary students preparing for **KSSM SPM** (Form 4–5 Physics, Chemistry, Biology). It reasons about *what the student is confused about* and *the pedagogically-correct way to fix it*, then assembles a faithful interactive from a pre-built component library — instead of returning a wall of text.

---

## 2. The problem (Malaysian-grounded)

1. **Abstract-concept mastery + resource constraints.** The KSSM SPM science syllabus requires visualising microscopic/abstract processes (osmosis, bonding, stoichiometry, forces). Underfunded — especially rural / B40 — schools often lack equipped labs, leaving students to memorise experiments from static textbook diagrams.
2. **Unaddressed, documented misconceptions.** Malaysian science students carry persistent, well-documented misconceptions (e.g. "osmosis is water moving to where there's more water"). Generic chatbots and static tools do not *diagnose* these specific errors — they emit text students copy without comprehension.

**Target users:** Form 4 & 5 science-stream students sitting SPM; and their science teachers.

---

## 3. Why this is defensible (vs general-purpose GenUI)

General-purpose GenUI (e.g. Gemini dynamic view) is **general-purpose and stateless per prompt** — it renders a nice interface for *this* question and forgets. Synapse owns three gaps a generic tool structurally won't touch:

1. **The pedagogy gap** — a learning-science model decides the intervention (the Diagnostician + Strategist), not a topic-matcher. → scores *Educational Significance*.
2. **The component-quality gap** — faithful, domain-correct KSSM sims, not generic widgets. → the moat.
3. **The persistent-learner-model gap** — remembers what you got wrong, what representation clicked, what's due for spaced repetition. → makes it a *system*, not a lookup.

The **wow** lives in *visible agentic reasoning*, the part we are best equipped to build — not in out-rendering Google.

---

## 4. Architecture

### 4.1 Runtimes (ADR-008)
Monorepo, two runtimes joined by an SSE contract:

```
Student ── HTTP/SSE ──▶ Next.js frontend ── HTTP/SSE ──▶ FastAPI backend ──▶ LangGraph pipeline
   ▲                        │  renders typed component blocks        │  4 agents + provider router
   └──── interaction events ┘                                        └──▶ learner store + misconception KB
```

- **Backend** (`backend/`): FastAPI + LangGraph. Owns the agents, the provider router, the component *registry* (the catalog the composer selects from), the misconception knowledge base, and the learner store.
- **Frontend** (`frontend/`): Next.js App Router. Owns the *implementations* of the interactive components and the SSE renderer that maps streamed blocks → React components.

### 4.2 The streaming contract (ADR-010 — load-bearing)
The backend streams **typed component blocks** as SSE events. Each block:

```jsonc
{
  "type": "component_block",
  "pattern": "gradient-diffusion-sandbox",   // key into the frontend library
  "props": { /* pattern-specific, validated by Pydantic on send */ },
  "meta": { "subject": "Biology", "form": 4, "topic": "osmosis", "strategy": "contrasting-cases" }
}
```

Agent-reasoning steps stream as their own event type (`agent_step`) so the UI can render the pipeline thinking live (constraint #3). The schema lives in `backend/app/models/schemas.py`; the frontend mirror + pattern→component map lives in `frontend/lib/blocks.ts`. **These two must stay in sync (D-10).**

### 4.3 Provider strategy (ADR-011)
No hard-coded default provider. Each agent names a **primary + ordered fallback chain** in `backend/app/providers/config.py`; the router (`providers/router.py`) executes the chain, falling through on error/refusal, and logs provider + token/cost. Adding or reordering a provider is a config edit, never a code change in an agent.

### 4.4 Learner state (ADR-012, D-11)
Persistent per-student profile: diagnosed misconceptions, mastery per topic, which representations worked, spaced-repetition schedule. **SQLite for local dev; Firebase for the hosted demo** — behind a `LearnerStore` interface so the backend doesn't care which is live.

---

## 5. The four agents

The pipeline is a LangGraph `StateGraph` over a shared `PipelineState` (Pydantic). Forward edges compose; the tutor loop closes back.

### 5.1 Diagnostician
- **In:** student question + learner profile + the KSSM misconception library for the detected topic.
- **Out:** `Diagnosis { kind: misconception | knowledge_gap | mastery_check, topic, subject, form, misconception_id?, confidence }`.
- **Grounding:** must match against pre-authored misconceptions (constraint #6), not improvise.

### 5.2 Pedagogy Strategist
- **In:** diagnosis.
- **Out:** `Strategy { technique, target_pattern, rationale }` where `technique ∈ {contrasting-cases, predict-observe-explain, worked-example-fading, retrieval-practice, labelled-exploration}`.
- Chooses the pedagogically-correct move; a misconception → *don't explain, contrast*; a gap → *worked example*; etc.

### 5.3 Component Composer
- **In:** strategy + the component registry.
- **Out:** a validated `ComponentBlock` (pattern + props + meta). Selects the pattern, configures its parameters (particles, membrane rules, labels, presets) to enact the strategy.

### 5.4 Tutor Loop
- **In:** interaction events from the composed component (predictions, slider values, quiz answers).
- **Out:** a learner-profile update + spaced-repetition scheduling; informs the *next* composition.

---

## 6. The component library (the moat)

Pre-built, faithful, **parameterised by interaction pattern** (constraint #2). Each pattern is one React component + one registry entry (schema of its props + which topics/strategies it serves).

**The 12 locked demo concepts (D-13) map to 14 patterns** — full spec in **`concept-catalog.md`** (the build manifest), mirrored in `backend/app/components/registry.py`:

| Pattern | Serves | Subject(s) |
|---|---|---|
| `gradient-diffusion-sandbox` | osmosis / water in plants (turgor, plasmolysis) — **flagship** | Biology |
| `electron-bonding-explorer` | bonding & electrons (ionic vs covalent) — **flagship** | Chemistry |
| `force-motion-sim` | forces & motion (ticker tape, v-t graph) — **flagship** | Physics |
| `stage-sequencer` | cell division (mitosis / meiosis) | Biology |
| `process-timeline` | menstrual cycle & egg movement | Biology |
| `labelled-diagram-explorer` | digestive system (journey), cell/heart diagrams | Biology/Chem |
| `matching-pairs` | enzyme↔substrate (supports digestive) | Biology/Chem |
| `punnett-square-builder` | genetics & inheritance | Biology |
| `signal-pathway-sim` | neuron / impulse / reflex arc | Biology |
| `atomic-structure-explorer` | atomic structure (nucleus + shells) | Chemistry |
| `reaction-lab-sandbox` | reactions with apparatus + ingredients | Chemistry |
| `circuit-builder-sandbox` | electricity (Ohm's law, series/parallel) | Physics |
| `wave-optics-sandbox` | waves & optics (ripple tank, ray diagrams, lenses) | Physics |
| `quick-check-quiz` | retrieval practice across any topic | all |

Faithfulness is per-component non-negotiable (constraint #1): a concept is "live" only when its science is correct, not merely when it renders. Build order prioritises the 3 flagships so there is always a flawless fallback demo (see `concept-catalog.md`).

---

## 7. Non-negotiable pedagogical principles (citable)

Predict-observe-explain · contrasting cases · productive failure · worked-example fading · retrieval practice · spaced repetition. The Strategist reasons *over* these; they are the *Educational Significance* claim, grounded in learning-science literature (see `synapse-sources.md`).

---

## 8. Responsible AI

- No hallucinated content — components are pre-built and domain-correct; the AI only selects/configures (constraint #1).
- Diagnosis is grounded in a citable misconception library, not improvisation.
- Human oversight: teacher-facing view of what was diagnosed and why (roadmap).
- Multilingual path: Bahasa Malaysia interface strengthens the local-access angle (roadmap).

---

## 9. Roadmap / build sequence

| Phase | Scope | Exit criteria |
|---|---|---|
| **P0** | Foundation — this skeleton | Both runtimes boot; SSE contract defined + typed; LangGraph graph runs with stub nodes emitting scripted `agent_step` + one `component_block`; landing page renders the Synapse identity. |
| **P1** | One live vertical slice (osmosis) | Real Diagnostician→Strategist→Composer over **Anthropic Claude** via the router (D-14); live `gradient-diffusion-sandbox` renders from streamed props; Tutor Loop writes one profile update. |
| **P2** | The 12 concepts (D-13) | All 12 locked concepts built as real interactives, **flagships first** (osmosis · bonding-electrons · forces-motion), each domain-correct + teacher-checked. See `concept-catalog.md`. |
| **P3** | Learner model + spaced repetition | Persistent profile informs the next composition; SR schedule surfaces due topics. |
| **P4** | Polish + demo script | 8-min demo beat sheet; latency < 3s time-to-first-token via streaming. |
| **P5** | Second-hackathon framing | Codex-KL vs hackAstone pitch variants; Bahasa Malaysia stretch. |

---

## 10. Decision Log (canonical list — details in `changelog/DECISIONS.md`)

| # | Decision |
|---|---|
| D-01 | Agents select/configure pre-built components; never generate UI from scratch. |
| D-02 | Component library is parameterised by interaction pattern, not by topic. |
| D-03 | Agent reasoning is streamed and visible — the pipeline is the demo. |
| D-04 | Diagnosis is grounded in a pre-authored KSSM misconception library. |
| D-05 | All LLM calls go through a config-driven multi-provider router; **Anthropic Claude is the live primary** (see D-14). |
| D-06 | ~~Demo scope is brutally narrow (1 subject deep).~~ **Superseded by D-13** — the demo now covers all 12 concepts across 3 subjects; the *depth-first, flagships-first* discipline it protected is preserved as the build order. |
| D-07 | One codebase, two hackathon framings (Codex KL / hackAstone). |
| D-08 | Monorepo: Python FastAPI+LangGraph backend + Next.js frontend, joined by SSE. |
| D-09 | Frontend owns component *implementations*; backend owns the *registry* it selects from. |
| D-10 | Typed component-block schema is the seam; backend schema + frontend mirror stay in sync. |
| D-11 | Learner store behind an interface: SQLite (dev) → Firebase (hosted demo). |
| D-12 | Python 3.13 + bun for the two runtimes (matches team tooling). |
| D-13 | Demo covers **all 12 locked concepts** (3 Chem · 3 Phys · 6 Bio) as real interactives; flagships-first build order (see `concept-catalog.md`). |
| D-14 | **Anthropic Claude is the live primary provider** (Haiku for Diagnostician/Composer, Sonnet for Strategist); OpenAI is the configured fallback. |
| D-15 | Product name stays **Synapse**; layout stays the **centered** `Synapse_Demo.html` shape. The UI/UX team's "TutorLah!" sidebar prototype is superseded; salvage its per-subject colour theming only. |

---

## 11. Open questions

- **OQ-1:** Which single subject/topic is the P1 flagship — lock osmosis (Biology) as assumed, or Physics forces? *(ASSUMED: osmosis — it is the mockup flagship and has the cleanest predict-observe-explain moment.)*
- **OQ-2:** ~~Which provider is each agent's primary?~~ **Resolved (D-14):** Anthropic Claude — Haiku for Diagnostician/Composer (fast/structured), Sonnet for the Strategist (reasoning-heaviest). OpenAI is the fallback. Confirm exact model ids against the Claude API skill in P1.
- **OQ-3:** Firebase now or SQLite-only through the hackathon demo? *(ASSUMED: SQLite through P3; Firebase only if a hosted multi-device demo is needed.)*
- **OQ-4:** How much of the agent reasoning is genuinely LLM-driven vs scripted for the P0/demo? *(P0 = scripted stubs; P1 = genuinely LLM-driven for the osmosis slice.)*

---

## 12. Team & context

- **Team:** Dang Wangi (UTP). Lead: Fakhrul Azim (AI/ML, agent workflows, backend).
- **Codex Community Hackathon KL 2026** — Education Access track; Demo Day 18 July 2026 (Sunway University). Framing: Malaysian SPM user + B40 lab-gap equity.
- **hackAstone 2026** — "Agentic AI for Education"; submission 1 July, finals Amsterdam Oct 2026. Framing: agentic pedagogy + academic novelty.
- **Post-hackathon:** Azim's FYP at UTP; user-evaluation studies; open-source / SaaS path.

See `../Codex hackathon/` and `../Hackastone/` for the full hackathon context references.
