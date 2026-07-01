# Synapse — Build Status

> **Read this first to know where we are.** Updated at the end of every build session. Phases and scope come from `refdocs/synapse-prd.md` §9. Don't reorder phases without updating this file and saying why (CLAUDE.md "keep docs current").

**Build philosophy:** the pipeline is the product — wire one agent step end-to-end (question → agent_step stream → one composed component_block → learner-model write) before adding a second agent's real logic or a second component. Never start the next phase until the current one is green end-to-end. Depth over breadth (D-06).

---

## Phase checklist

| Phase | Scope | Status |
|---|---|---|
| **P0** | Foundation — monorepo skeleton, SSE contract, LangGraph stub graph, Next.js shell + landing, provider-router / registry / misconception stubs | ✅ **Scaffolded AND verified end-to-end (2026-07-01).** Backend: `pytest` 2/2 pass; live `POST /api/ask` streamed all 4 agents' `agent_step`s + the osmosis `component_block` + tutor-loop write over SSE. Frontend: `bunx tsc --noEmit` clean + `bun run build` clean (4 routes). See "P0 detail" below. |
| **P1** | One live vertical slice (osmosis) over Anthropic Claude | ✅ **Done + verified (2026-07-01).** Agents LLM-driven (grounded) with scripted fallback; router `run_structured()` + OpenAI fallback + `providers/metrics`; faithful `gradient-diffusion-sandbox` (predict-observe-explain); faithfulness pinned in code; SQLite store. `pytest` 9/9, `tsc` + `next build` clean, live `POST /api/ask` streamed the full sequence. Runs scripted with no key. See CHANGELOG 2026-07-01 P1. |
| **P2** | All 12 demo concepts as real interactives, flagships-first (D-13) | ✅ **Done (2026-07-01).** All 14 interaction patterns now have real, interactive React components wired through the seam (`lib/blocks.ts`). 3 flagships faithful (osmosis, forces-motion with ΣF=ma + live v-t graph, bonding-electrons contrasting cases). Long-tail concepts (menstrual cycle, cell division, digestive, genetics, neuron, atomic structure, circuits, waves/optics, reactions, quiz) ship as lighter-but-correct interactives per the D-13 allowance. `tsc` + `next build` clean, flagship routes verified. |
| **P3** | Learner model + spaced repetition | ✅ **Done (2026-07-01).** Components post interaction events back (`POST /api/interaction`); the Tutor Loop updates mastery and reschedules spaced repetition (correct → resolved + review pushed out; wrong → resurfaced sooner). The Diagnostician reads the profile — a cleared misconception flips the next visit to a mastery check. `GET /api/profile/{id}` drives an on-screen "Your progress" panel. Verified live: mastery rose to 0.34, misconception marked resolved, review pushed to 7 days, re-ask flipped to mastery check. |
| **P4** | Polish + demo script | ⬜ Not started |
| **P5** | Second-hackathon framing pass | ⬜ Not started |

---

## P0 — Foundation (current phase)

**What the skeleton contains (2026-07-01):**

### Backend (`backend/`)
| Piece | File | Status |
|---|---|---|
| FastAPI app + CORS + health | `app/main.py` | ✅ Scaffolded — `/health` + mounts the API router |
| SSE contract (typed blocks + agent steps) | `app/models/schemas.py` | ✅ Scaffolded — Pydantic v2 models: `PipelineState`, `Diagnosis`, `Strategy`, `ComponentBlock`, `AgentStep`, SSE event envelopes |
| LangGraph pipeline (4 nodes) | `app/agents/graph.py` + `agents/*.py` | ✅ Scaffolded — `StateGraph` wired Diagnostician → Strategist → Composer → TutorLoop; **nodes are scripted stubs** (emit deterministic diagnosis/strategy/block for the osmosis path), not yet LLM-driven |
| Provider router (multi-provider, no default) | `app/providers/router.py` + `providers/config.py` | ✅ Scaffolded — config-driven chain per agent; adapters are stubs that raise "not configured" until keys/impl added |
| Component registry (the catalog the composer picks from) | `app/components/registry.py` | ✅ Scaffolded — seed entries for the 6 PRD patterns with prop schemas |
| Misconception knowledge base | `app/knowledge/misconceptions.py` | ✅ Scaffolded — seed KSSM misconceptions incl. the osmosis inverted-gradient one |
| Learner store interface | `app/store/learner_store.py` | ✅ Scaffolded — `LearnerStore` protocol + in-memory dev impl (SQLite/Firebase deferred, D-11) |
| SSE streaming route | `app/api/routes.py` | ✅ Scaffolded — `POST /api/ask` runs the graph and streams `agent_step` + `component_block` events |

### Frontend (`frontend/`)
| Piece | File | Status |
|---|---|---|
| Next.js shell + config | `next.config.ts`, `tsconfig.json`, `package.json`, `postcss.config.mjs` | ✅ Scaffolded |
| Design tokens + globals | `app/globals.css` | ✅ Scaffolded — Synapse palette (indigo/teal) ported from `../Synapse_Demo.html` |
| Root layout | `app/layout.tsx` | ✅ Scaffolded |
| Landing page (Synapse identity) | `app/page.tsx` | ✅ Scaffolded — topbar + logo mark + hero + prompt card + scenario chips, matching the demo |
| SSE client + block schema mirror | `lib/client.ts`, `lib/blocks.ts`, `lib/types.ts` | ✅ Scaffolded — mirrors backend schema; `pattern → component` map |
| Agent pipeline panel (visible reasoning) | `components/AgentPipeline.tsx` | ✅ Scaffolded — renders streamed `agent_step` cards |
| Component library (by pattern) | `components/library/*` | ✅ Scaffolded — one placeholder component per seed pattern + a `BlockRenderer` |

**Verified this session (2026-07-01):** both runtimes were dependency-installed and booted on this machine. Backend `pytest` → 2/2 pass; a live `POST /api/ask` (uvicorn on :8123) streamed the full sequence — 4 agents' reasoning steps → the `gradient-diffusion-sandbox` component block (faithful osmosis props: `correct_direction: toward-higher-solute`) → the tutor-loop profile write → `done`. Frontend `bunx tsc --noEmit` clean and `bun run build` clean (`/` at 4.62 kB). The backend↔frontend SSE seam (D-10) is proven, not just typed.

**Deliberately deferred to P1+ (not bugs):** agent nodes are scripted (no LLM); no provider adapter is wired to a real SDK (the router falls through to scripted behaviour when unconfigured); learner store is in-memory only. P0 is the runnable *shape*; P1 makes the osmosis slice genuinely live.

---

## How to run locally (once P0 is installed)

**Backend:**
1. `cd backend`
2. `uv sync` (or `pip install -e .`) — Python 3.13
3. copy `.env.example` → `.env` (provider keys optional until P1)
4. `uv run uvicorn app.main:app --reload --port 8000`
5. health check: `GET http://localhost:8000/health`

**Frontend:**
1. `cd frontend`
2. `bun install`
3. copy `.env.local.example` → `.env.local` (sets `NEXT_PUBLIC_API_BASE=http://localhost:8000`)
4. `bun dev` → open `http://localhost:3000`

Ask a question (or click a chip) → the frontend POSTs to the backend `/api/ask` → the stubbed graph streams agent-reasoning steps into the pipeline panel, then a component block that renders a placeholder from the library.

---

## How to update this file

After finishing a piece, flip its row to ✅ with a one-line note if anything deviated. After finishing a phase, flip the phase table row and promote the next phase to "current phase" with its own checklist.
