# Synapse, Project Description

> hackAstone 2026 written submission. Theme: Agentic AI for Education. Team Dang Wangi, UTP.
> Live demo: (deploy pending, see `decisions.md` P-a). Repo: this repository, `Synapse/`.

## One line

Synapse is a visible multi-agent tutor for Malaysian KSSM SPM science that diagnoses a student's
specific misconception, decides the pedagogically correct move, and composes a science-faithful
interactive experiment, streaming its reasoning live.

## The problem and the users

Malaysian SPM science students, Form 4 and Form 5, can recite definitions but carry stubborn
misconceptions (osmosis moves water to "more water"; a moving object needs a constant force). The
practical work that would fix this is hardest to deliver in B40 and rural schools with limited lab
access. Synapse gives every student a correct virtual experiment and the pedagogy that makes the
misconception fail visibly, on any device.

## The solution and the agentic architecture

A team of agents runs as a pipeline, and the pipeline is the product:

1. **Diagnostician** matches the question against a sourced KSSM misconception knowledge base and
   returns a grounded diagnosis (it classifies into the KB, it never invents a misconception).
2. **Pedagogy Strategist** picks the learning-science intervention (contrasting cases,
   predict-observe-explain, worked-example fading, retrieval practice) and names it on screen.
3. **Component Composer** selects a pre-built, KSSM-faithful component and configures its
   parameters. It outputs a component pattern plus validated props, never markup.
4. **Tutor Loop** records the interaction, updates mastery, and schedules spaced repetition, so the
   next composition is informed by history.

All model calls go through a config-driven provider router (Anthropic Claude primary, OpenAI
fallback) with per-call cost and latency logging. The whole thing degrades gracefully to scripted
logic when no API key is present, so it always runs.

## How Synapse answers the four judging dimensions

### Innovation and Novelty

The novelty is **pedagogy-driven composition with visible reasoning**, not topic-matching. Generic
GenUI generates UI one-shot and hides its reasoning; Synapse foregrounds a live "reasoning theatre"
(Diagnostician to Strategist to Composer) and names the pedagogical decision on screen ("this is a
misconception, not a gap, so contrast cases"). It **selects and configures pre-built components; it
never generates UI**, which is the honest, defensible architecture and eliminates hallucinated
science. That combination, grounded diagnosis plus visible pedagogy plus select-not-generate, is
what a generic dynamic view structurally cannot do.

### Technical Readiness Level

A working full-stack product, verified by running, not just described:

- FastAPI + LangGraph backend streaming typed component blocks over SSE; Next.js + TypeScript
  frontend with a 14-pattern faithful component library.
- Structured output with a repair pass and validation; the science-critical fields are pinned in
  code, so a wrong model answer cannot ship a wrong sim.
- Provider fallback (Anthropic to OpenAI to scripted) and per-call observability
  (`GET /api/metrics`).
- Test coverage for agent contracts, JSON extraction and repair, SSE serialisation, the learner
  store and spaced repetition (12 passing tests). Frontend typecheck and production build clean.
- Deploy configuration prepared (backend Dockerfile, frontend Vercel config); public URL is the
  final step (pending host selection).

### Commercial Viability

Clear path to adoption: free for students (growth), a teacher dashboard that turns a class into a
readable heatmap and pulls schools in (B2B2C), then school and district licences. The B40 lab-access
wedge aligns with existing equity priorities. The moat is the faithful pattern library plus the
sourced misconception KB, which scales across the syllabus as configuration rather than new code.
Full detail in `GO-TO-MARKET.md`.

### Educational Significance and Applicability

Grounded, citable pedagogy. The misconception KB carries real sources (Odom and Barrow on osmosis;
Taber on chemical bonding; Clement and Halloun-Hestenes on force; Driver on photosynthesis;
Shipstone on circuits). Each strategy names its learning-science technique. Concepts are tagged with
KSSM subject and form. A concrete evaluation plan (pre/post two-tier diagnostic with a one-week
retention test) is in `EVALUATION-PLAN.md`. Applicability to real classrooms is designed in: a
teacher view, planned Bahasa Malaysia interface, keyboard-navigable interactives, and a
lightweight client that works on the phones students actually have.

## Responsible AI

- **No hallucinated content:** the agents select and configure pre-built components; they never
  generate the science. Faithfulness is pinned in code.
- **Grounded diagnosis:** the Diagnostician classifies into an explicit, sourced KB, not free
  improvisation.
- **Human oversight:** the teacher view keeps a human in the loop over each learner's model.
- **Data and privacy:** the learner profile stores only a pseudonymous student id, topic mastery,
  and misconception history; no personal data is required to use the student view. Server-side keys
  only; nothing sensitive reaches the client.

## Tech stack

Backend: Python 3.13, FastAPI, LangGraph, Pydantic v2, SSE (sse-starlette), a provider router over
Anthropic and OpenAI, SQLite learner store (Firebase-ready behind the interface). Frontend:
Next.js App Router, TypeScript, a pattern-based interactive component library, an SSE client that
renders streamed typed blocks, bun.

## Team

Team Dang Wangi, Universiti Teknologi PETRONAS (UTP).

## Links

- Repository: `Synapse/` in this repository.
- Live demo: to be added once deployed (backend host + Vercel frontend; see `decisions.md`).
- Key docs: `GO-TO-MARKET.md`, `EVALUATION-PLAN.md`, `VIDEO-SCRIPT.md`, `concept-catalog.md`,
  `synapse-prd.md`.
