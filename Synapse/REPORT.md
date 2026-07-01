# Synapse — Project Report

*A visible multi-agent pedagogical AI for Malaysian KSSM SPM science, by Team EduNova*

---

## Submission Details

| Field | Value |
|---|---|
| University | Universiti Teknologi PETRONAS (UTP) |
| Faculty / Programme | Computer Science (final-year students) |
| Course code / name | _[fill in]_ |
| Lecturer / Supervisor | _[fill in]_ |
| Team | EduNova |
| Team members | Fakhrul Azim (CEO) · Por Jie Hao (CTO) · Azrain Shawn (CTO) · Khaidhir (CEO) · Danish Iskandar (President) · Adam Iman (General Manager) · Nur Farah (General Manager) |
| Submission date | _[fill in]_ |
| Event / context | Codex Community Hackathon KL 2026 (Education Access) · hackAstone 2026 ("Agentic AI for Education") |

---

## 1. University Introduction

Universiti Teknologi PETRONAS (UTP) is a private university in Seri Iskandar, Perak, Malaysia,
established by PETRONAS with a focus on engineering, technology, and applied sciences. UTP places
strong emphasis on industry-linked, project-based learning, and its students regularly represent the
university at national and international hackathons and innovation competitions.

_[Placeholder — add specific course code/name and any course learning outcomes this report is being
submitted against, if required by the assignment brief.]_

This project, **Synapse**, was developed by **Team EduNova**, a team of seven UTP Computer Science
students in their final year, as an entry for two hackathons: **Codex Community Hackathon KL 2026**
(Education Access track) and **hackAstone 2026** (theme: Agentic AI for Education).

**Team EduNova:**

| Name | Role |
|---|---|
| Fakhrul Azim | CEO |
| Khaidhir | CEO |
| Por Jie Hao | CTO |
| Azrain Shawn | CTO |
| Danish Iskandar | President |
| Adam Iman | General Manager |
| Nur Farah | General Manager |

---

## 2. Project Background

### The problem

Malaysia's science curriculum has fundamentally shifted toward **Higher-Order Thinking Skills
(KBAT)** — moving away from rote memorisation toward deep conceptual understanding and application.
This reform relies on a crucial assumption: that students get regular, hands-on experience in science
labs to build correct mental models. In reality, severe inequalities in lab access exist, particularly
in rural and under-resourced schools — missing apparatus, large class sizes, and limited timetable
slots mean that for hundreds of thousands of SPM candidates each year, essential practical experiments
are reduced to teacher demonstrations or textbook diagrams. This creates a national-scale gap right
when exam structures demand true comprehension.

The gap breaks down into four compounding pillars:

1. **Incompetency of traditional learning environments** — rote-based teaching that doesn't build the
   conceptual mastery the KBAT curriculum now demands.
2. **Unequal access to crucial lab infrastructure** — B40 and rural schools lack the apparatus and
   time to run the practicals that build correct mental models.
3. **Persistent and hidden misconceptions** — students can recite definitions correctly (e.g. osmosis,
   force and motion) while still holding well-documented, wrong underlying mental models that surface-
   level quizzes fail to catch.
4. **Inadequate EdTech and AI solutions** — existing tools either generate generic content or act as
   opaque "black box" tutors, without transparent, verifiable pedagogical reasoning.

Fortunately, two forces are converging to provide a solution: the urgent need for accessible practical
science, and the maturation of Generative AI. Synapse sits precisely at this intersection.

### The idea

Synapse addresses this by giving every student a **correct, virtual experiment** paired with the
**right pedagogical intervention**, on any device. Rather than a single model "generating a UI" for a
topic — which risks hallucinated or scientifically incorrect content — Synapse uses a **pipeline of
specialised agents** that:

1. **Diagnose** the student's specific conceptual state against a sourced KSSM misconception
   knowledge base (never inventing a misconception).
2. **Decide** the learning-science-correct intervention (e.g. contrasting cases,
   predict-observe-explain, worked-example fading, retrieval practice).
3. **Compose** a science-faithful interactive by selecting and configuring a pre-built component from
   a curated library — the agents never generate UI markup from scratch.
4. **Track** the interaction over time, updating a persistent learner model and scheduling spaced
   repetition.

The differentiator is that this reasoning process is **streamed and visible** to the user in real
time — watching the Diagnostician, Pedagogy Strategist, and Component Composer "think" on screen —
rather than being hidden behind a single opaque generation step.

### Objectives

1. **Deliver targeted, pedagogically sound interventions** — move beyond generic repetition by
   dynamically applying precise learning-science strategies (e.g. contrasting cases for
   misconceptions, scaffolded examples for knowledge gaps), ensuring students build the true
   conceptual mastery the KBAT curriculum requires.
2. **Provide universal access to faithful virtual experiments** — deliver scientifically accurate,
   interactive virtual labs directly to the personal devices students already own, regardless of
   their school's funding or facilities.
3. **Diagnose root misconceptions with evidence-based precision** — replace surface-level quizzes
   with a KSSM-aligned diagnostic tool checked against a well-researched database of known scientific
   misconceptions, pinpointing specific flawed mental models rather than guessing.
4. **Make AI reasoning transparent and auditable** — eliminate the risk of AI hallucination and
   "black box" tutoring by streaming diagnostic and intervention choices live, building metacognitive
   awareness in students and giving teachers clear, verifiable oversight of every pedagogical
   decision.

### Why it matters

- **Educational significance:** the misconception knowledge base is grounded in cited
  science-education literature (e.g. Odom & Barrow on osmosis, Taber on chemical bonding, Clement &
  Halloun-Hestenes on force, Driver on photosynthesis, Shipstone on circuits), and each strategy names
  its underlying learning-science technique.
- **Equity:** targets students in B40 and rural schools who lack reliable access to physical lab
  equipment.
- **Responsible AI:** no hallucinated science — components are pre-built and faithfulness-pinned in
  code; the agents only select and configure, never freely generate.
- **Commercial path:** free for students, with a teacher dashboard (class-level mastery heatmap) as a
  B2B2C wedge toward school/district licensing.

---

## 3. Technical Implementation

### Repository

**GitHub:** [github.com/Azimlearning/GenUI-Education](https://github.com/Azimlearning/GenUI-Education)
(project code lives under the `Synapse/` directory of this repository)

### Architecture overview

Synapse is a monorepo with two runtimes joined by a Server-Sent-Events (SSE) contract of **typed
component blocks**:

```
frontend/   Next.js (App Router) · TypeScript · Tailwind · bun
            └─ the interactive component library + the SSE renderer

backend/    Python 3.13 · FastAPI · LangGraph · Pydantic v2
            └─ the 4 agents + provider router + component registry
               + misconception knowledge base + learner store
```

The backend streams **typed component blocks** (`{ pattern, props, meta }`) over SSE; the frontend
maps each `pattern` to a React component in its library and hydrates it with the streamed `props`.
This schema is the load-bearing contract between the two runtimes.

### The agent pipeline

| Agent | Role | Reads | Writes |
|---|---|---|---|
| **Diagnostician** | Identifies the student's specific misconception / knowledge gap / mastery level | Question + learner profile + misconception library | A diagnosis |
| **Pedagogy Strategist** | Selects the correct pedagogical intervention | Diagnosis | A strategy + target interaction pattern |
| **Component Composer** | Selects and configures a component from the library | Strategy + component registry | A typed component block (streamed via SSE) |
| **Tutor Loop** | Observes the interaction, updates the learner model, schedules spaced repetition | Interaction events | Learner-profile update |

Data flows forward (question → diagnosis → strategy → composed component) and the tutor loop closes
it backward (interaction → learner model → informs the next composition).

### Key technical decisions

- **Select, don't generate:** agents choose and parameterise pre-built, KSSM-faithful components
  rather than generating UI/markup from a model, eliminating hallucinated science by construction.
- **Interaction-pattern parameterisation:** components are built around ~12–18 reusable interaction
  patterns (e.g. one gradient/diffusion sandbox serves osmosis, dialysis, and gas exchange) rather
  than one bespoke component per topic — this is what lets the library scale across the syllabus as
  configuration, not new code.
- **Multi-provider LLM router:** every LLM call goes through a config-driven provider router
  (Anthropic Claude as primary — Haiku for the Diagnostician/Composer, Sonnet for the Strategist —
  with OpenAI as fallback), with per-call cost/latency logging (`GET /api/metrics`). No agent calls a
  provider SDK directly.
- **Graceful degradation:** with no API key configured, agents fall back to scripted logic so the
  application always runs end-to-end; setting `ANTHROPIC_API_KEY` switches to live model reasoning.
- **Server-side keys only:** API keys are read only in the Python backend and are never exposed to
  the Next.js client.
- **Grounded diagnosis:** the Diagnostician classifies against an explicit, sourced misconception
  knowledge base (`backend/app/knowledge/`) rather than improvising a diagnosis freely.

### Tech stack

**Backend:** Python 3.13, FastAPI, LangGraph (agent orchestration), Pydantic v2 (typed agent state
and component blocks), SSE via `sse-starlette`, a provider router over Anthropic and OpenAI, and a
SQLite learner store (designed to be Firebase-ready behind the same interface).

**Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, a pattern-based interactive component
library (`frontend/components/library/`), an SSE client that renders streamed typed blocks, and `bun`
as the package manager/runtime.

### Current status

The pipeline is live end-to-end with LLM-driven agents (and a scripted fallback). All 12 target
concepts render as real interactives, with three fully faithful flagship demos: **osmosis**,
**forces-motion**, and **bonding-electrons**. The learner loop closes (mastery tracking + spaced
repetition, informed by history), and a teacher dashboard is available at `/teacher`. The backend has
12 passing tests; the frontend typechecks and builds cleanly.

### Running the project locally

```bash
# Backend
cd Synapse/backend
uv sync
cp .env.example .env          # optional: set ANTHROPIC_API_KEY for live model reasoning
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd Synapse/frontend
bun install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE=http://localhost:8000
bun dev                             # http://localhost:3000
```

---

## 4. Educational Significance

Synapse's pedagogy is grounded, not improvised. The misconception knowledge base cites real
science-education literature per concept — Odom & Barrow on osmosis, Taber on chemical bonding,
Clement and Halloun-Hestenes on force and motion, Driver on photosynthesis, Shipstone on circuits —
and every strategy the Pedagogy Strategist picks names its underlying learning-science technique
(contrasting cases, predict-observe-explain, worked-example fading, retrieval practice) rather than
being a generic "explanation."

**Evaluation design.** A concrete pre/post study is designed (`refdocs/EVALUATION-PLAN.md`), sized
for a hackathon-to-FYP timeline:

- **Participants:** 10–15 Form 4/5 students, prioritising B40 and rural students.
- **Design:** within-subjects pre-test → intervention → immediate post-test → delayed post-test one
  week later, on the three flagship concepts (osmosis, forces and motion, bonding).
- **Instrument:** a two-tier diagnostic (answer + reason), which separates "right answer, wrong
  reason" from genuine conceptual understanding — the exact failure mode Synapse targets.
- **Primary outcome:** normalised gain in correct-answer-and-correct-reason items, pre vs post, with
  a one-week retention check that the spaced-repetition scheduling is designed to support.
- **Control comparison:** where feasible, a static-explanation control isolates the value of the
  predict-observe-explain pedagogy itself, not just correct information.

**Applicability to real classrooms** is designed in from the start: a teacher view for human
oversight of each learner's diagnosed misconceptions and mastery, a planned Bahasa Malaysia
interface, keyboard-navigable interactives, and a lightweight client that runs on the phones
students already own rather than requiring lab hardware.

## 5. Commercial Viability

**Market.** Primary users are Malaysian KSSM SPM science students (Form 4–5, Physics/Chemistry/
Biology) — a cohort of roughly 380,000–400,000 SPM candidates per year. The wedge is B40 and rural
lab access: practical work that under-resourced schools cannot deliver (osmosis potato experiments,
ticker-tape trolleys, titrations, ripple tanks) becomes a scientifically-correct virtual experience
on any device.

**Defensible moat.** Not raw generation — a general-purpose model out-resources any startup there.
The moat is the **faithful, KSSM-aligned component library plus the sourced misconception knowledge
base**: 14 interaction patterns already cover 12 concepts across 3 subjects, and new topics are
added as *configuration*, not new code, since components are parameterised by interaction pattern
rather than by topic. Correctness is pinned in code, so a wrong sim (a trust-killer in education)
cannot ship.

**Adoption path:**

1. **Free tier for students (bottom-up growth)** — the shareable "aha" moment drives word-of-mouth.
2. **Teacher dashboard as the B2B2C wedge** — `/teacher` turns a class of 40 into a readable
   mastery/misconception heatmap, giving teachers a reason to pull the tool into their school.
3. **School and district licences (B2B)** — per-seat/per-cohort pricing for teacher analytics,
   class management, and a Bahasa Malaysia interface; tuition centres are a fast second channel.
4. **Ministry/state pilots** — the B40 lab-access story aligns with existing equity priorities,
   which is the credible route to scale funding.

**Pricing hypothesis:** student access stays free or low-cost by design (monetise the institution,
not the disadvantaged student); school licences carry the teacher dashboard, BM interface, and
cohort reporting, with volume discounts at district scale.

**Continuation path:** Synapse doubles as a final-year-project vehicle — the misconception KB and
the evaluation study above are publishable, and the pattern-library architecture is a reusable
research contribution, supporting an open-source-core-plus-hosted-SaaS path beyond the hackathon.

---

## References / Further Reading

- [`refdocs/synapse-prd.md`](refdocs/synapse-prd.md) — full product requirements document (source of truth)
- [`refdocs/PROJECT-DESCRIPTION.md`](refdocs/PROJECT-DESCRIPTION.md) — hackAstone written submission
- [`refdocs/concept-catalog.md`](refdocs/concept-catalog.md) — the 12 demo concepts and their interaction patterns
- [`refdocs/EVALUATION-PLAN.md`](refdocs/EVALUATION-PLAN.md) — full pre/post evaluation study design (source for §4)
- [`refdocs/GO-TO-MARKET.md`](refdocs/GO-TO-MARKET.md) — full commercial/go-to-market plan (source for §5)
- [`README.md`](README.md) — repository overview and run instructions
- `EduNova for HackAStone.pdf` — team pitch deck (problem statement, objectives, team, live demo)
