# Execution — P0 Foundation (skeleton)

> **How & in what order.** Plan: `plans/2026-07-01-p0-foundation.md`. Update this to match reality if it deviates (CLAUDE.md rule 4).

## Order of work (as built, 2026-07-01)

1. **Docs first.** `CLAUDE.md` + `refdocs/` (PRD, STATUS, sources, changelog, this plan/execution). The PRD fixes the four agents, the SSE contract shape, and the seed patterns so the code has a spec.
2. **Backend contract.** `app/models/schemas.py` — the Pydantic v2 models are written before anything that uses them, because they are the seam: `PipelineState`, `Diagnosis`, `Strategy`, `ComponentBlock`, `AgentStep`, and the SSE event envelope.
3. **Backend data stubs.** `providers/config.py` + `router.py`, `components/registry.py`, `knowledge/misconceptions.py`, `store/learner_store.py` — the things the agents read/write, stubbed with seed data.
4. **Backend agents.** `agents/{diagnostician,pedagogy_strategist,component_composer,tutor_loop}.py` as scripted functions over `PipelineState`, then `agents/graph.py` wires them into a LangGraph `StateGraph`.
5. **Backend edge.** `api/routes.py` runs the graph and yields SSE events; `main.py` mounts it with CORS for the Next.js origin.
6. **Frontend shell.** config (`package.json`, `tsconfig.json`, `next.config.ts`, `postcss.config.mjs`), `app/globals.css` (ported tokens), `app/layout.tsx`.
7. **Frontend contract mirror.** `lib/types.ts` + `lib/blocks.ts` (pattern→component map) + `lib/client.ts` (SSE reader).
8. **Frontend UI.** `components/AgentPipeline.tsx`, `components/library/*` placeholders + `BlockRenderer.tsx`, then `app/page.tsx` (landing matching the demo).

## Contract shape (the seam)

SSE events over `POST /api/ask` (body `{ question, student_id? }`):

- `agent_step` — `{ agent, status, detail }` — one per node as it reasons (drives the visible pipeline).
- `component_block` — `{ pattern, props, meta }` — the composed interactive (one per ask in P0).
- `done` — terminal.

Frontend maps `component_block.pattern` → `LIBRARY[pattern]` React component, hydrates with `props`.

## Verification done in P0

- Files created and internally cross-referenced (imports/paths consistent).
- **NOT yet:** dependency install or runtime boot on this machine (recorded as the open P0 item in STATUS.md). Next session: `uv sync` + `bun install`, boot both, confirm one ask streams through end-to-end, then flip the P0 row to ✅ and open P1.

## Handoff to P1

- Replace the scripted body of each agent with a real LLM call via `providers.router.run(agent=...)`.
- Wire one real provider adapter (per OQ-2 config).
- Implement the `gradient-diffusion-sandbox` for real (faithful osmosis) and have the Composer emit its props.
- Swap the in-memory learner store for SQLite.
