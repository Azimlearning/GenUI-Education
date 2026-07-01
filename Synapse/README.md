# Synapse

> **Visible multi-agent pedagogical AI for Malaysian KSSM SPM science (Form 4–5 Physics · Chemistry · Biology).**
> A team of agents diagnoses a student, decides the pedagogically-correct move, and *composes* an interactive learning experience from a pre-built component library — streamed live to the browser as Generative UI.

Google generates a UI for a topic. **Synapse orchestrates a team of pedagogical agents that diagnose a student and compose the right interactive — and you can watch them do it.**

Built by **Team Dang Wangi** (Universiti Teknologi PETRONAS) for **Codex Community Hackathon KL 2026** (Education Access) and **hackAstone 2026** ("Agentic AI for Education").

---

## What it does

1. A student asks a question in their own words (e.g. *"osmosis is when water moves to where there's more water"* — a real KSSM misconception).
2. A **Diagnostician** agent identifies the specific conceptual state (misconception / knowledge gap / mastery check), grounded in a pre-authored KSSM misconception library.
3. A **Pedagogy Strategist** picks the learning-science-correct intervention (e.g. contrasting cases, predict-observe-explain).
4. A **Component Composer** selects and configures a faithful interactive from the component library.
5. The student interacts (predicts, drags a slider, runs the sim) and the **Tutor Loop** updates their persistent profile and schedules spaced repetition.

The agent reasoning is **streamed and visible** — that is the differentiator, and the demo wow.

---

## Architecture

Monorepo, two runtimes joined by a Server-Sent-Events contract of **typed component blocks**:

```
frontend/   Next.js (App Router) · TypeScript · Tailwind · bun
            └─ the interactive component library + the SSE renderer

backend/    Python 3.13 · FastAPI · LangGraph · Pydantic v2
            └─ the 4 agents + provider router + component registry
               + misconception knowledge base + learner store
```

- The backend **selects and configures** pre-built components; it never generates UI from scratch.
- The component library is parameterised **by interaction pattern**, not by topic (one gradient/diffusion sandbox serves osmosis, dialysis, gas exchange…).
- All LLM calls go through a **config-driven multi-provider router** (no hard-coded default).

Full detail: [`refdocs/synapse-prd.md`](refdocs/synapse-prd.md). Current build state: [`refdocs/STATUS.md`](refdocs/STATUS.md).

---

## Status

**P0 — Foundation skeleton (scaffolded 2026-07-01).** Both runtimes are scaffolded and internally consistent; the LangGraph pipeline runs with **scripted stub nodes** and streams the visible reasoning + one placeholder component. Not yet dependency-installed or booted; no LLM wired yet. The next phase (P1) makes the osmosis slice genuinely live. See [`refdocs/STATUS.md`](refdocs/STATUS.md).

---

## Run locally

### Backend
```bash
cd backend
uv sync                       # Python 3.13 (or: pip install -e .)
cp .env.example .env          # provider keys optional until P1
uv run uvicorn app.main:app --reload --port 8000
# health: http://localhost:8000/health
```

### Frontend
```bash
cd frontend
bun install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE=http://localhost:8000
bun dev                            # http://localhost:3000
```

Ask a question (or click a scenario chip) → watch the pipeline reason → a component renders from the library.

---

## Repository layout

```
Synapse/
├── CLAUDE.md               # operating brief (read first each session)
├── README.md
├── refdocs/                # PRD (source of truth), STATUS, changelog, plans, execution, sources
├── backend/                # FastAPI + LangGraph
│   └── app/
│       ├── main.py
│       ├── api/            # SSE /api/ask route
│       ├── agents/         # diagnostician, pedagogy_strategist, component_composer, tutor_loop, graph
│       ├── providers/      # multi-provider router + config
│       ├── components/     # registry (the catalog the composer selects from)
│       ├── knowledge/      # KSSM misconception library
│       ├── store/          # learner store (interface + in-memory dev impl)
│       └── models/         # Pydantic schemas (the SSE contract)
└── frontend/               # Next.js
    └── app/ · components/library/ · lib/
```

---

*Concept references (design mockup, hackathon context, ideation) live one level up in `Genui/`.*
