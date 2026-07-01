# Plan — P0 Foundation (skeleton)

> **What to build & why.** Companion execution doc: `execution/2026-07-01-p0-foundation.md`.
> Status: scaffolded 2026-07-01 (not yet run). Tracks PRD §9 P0.

## Goal

A runnable *shape* of Synapse: both runtimes boot, the SSE contract is typed and shared, the LangGraph pipeline runs end-to-end with **scripted** nodes, and the landing page carries the Synapse identity. No LLM, no real provider, no persistence yet — those are P1+. This de-risks the seam (SSE typed blocks between Python and Next.js) and gives every later phase a place to slot into.

## Why this shape

- The **hardest integration risk** is the cross-runtime seam, so P0 exists to prove it: a question flows Next.js → FastAPI → LangGraph → back as streamed `agent_step` + `component_block` events → rendered by the frontend library. Get the shape right before any agent is smart.
- Scripted stubs let us build and see the *whole* loop (constraint #3, visible reasoning) without waiting on prompt engineering or keys.
- The provider router, component registry, and misconception KB are stubbed *now* so P1 only has to fill them in, not invent their shape.

## Deliverables

1. Docs system (`CLAUDE.md`, `refdocs/*`) mirroring the OmniX conventions. ✅
2. Backend skeleton (FastAPI + LangGraph stub graph + router/registry/KB/store stubs + SSE route). ✅
3. Frontend skeleton (Next.js shell + Synapse landing + SSE client + pipeline panel + library placeholders). ✅
4. This plan + its execution doc. ✅

## Non-goals for P0

- Real LLM calls / prompt engineering (P1).
- Faithful component physics (P2).
- Persistence beyond in-memory (P3).
- Auth, teacher view, Bahasa Malaysia (later).

## Exit criteria

- `uv run uvicorn app.main:app` serves `/health` and `/api/ask` streams events.
- `bun dev` renders the landing page; asking a question shows the pipeline reasoning then a placeholder component.
- Backend Pydantic block schema and frontend `blocks.ts` mirror agree (D-10).
