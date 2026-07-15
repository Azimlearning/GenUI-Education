# CLAUDE.md — Axiom Project Instructions

This file governs how you (the coding agent) work in this repository. Read it at the start of every session.

## What this project is

Axiom is a Tier 3 generative UI science learning app. Users ask science questions; the system streams a text explanation and generates a verified, interactive HTML/JS artifact (simulation, explorable diagram, experiment, visualization) rendered in a sandboxed iframe. Full spec: `docs/super-prompt-tier3-science-app.md`. Architecture: `docs/SYSTEM_ARCHITECTURE.md`. Current phase and task list: `docs/PLANNING.md`.

## Hard rules (never violate)

1. No unverified artifact may reach the client. The delivery path must be structurally unable to bypass the Verifier.
2. The artifact iframe uses `sandbox="allow-scripts"` only. Never add `allow-same-origin`.
3. Generated code libraries are served from `/vendor/` (same origin). Never introduce runtime CDN fetches.
4. Do not add a predefined component library for learning artifacts. Tier 3 or degrade to text.
5. Do not reorder build phases or start a phase before the previous phase's definition of done is met.
6. If the spec conflicts with reality, stop and surface the conflict. Do not silently deviate.

## Repository layout

```
/frontend        Next.js 14 App Router, TypeScript, Tailwind
/backend         FastAPI, LangGraph pipeline, Postgres via SQLAlchemy
/backend/prompts Generator, Verifier, Planner, Router, Explainer, Tutor prompts (markdown, loaded at runtime)
/backend/postprocess.py   Deterministic output fixes; grows over time
/vendor          Pinned local copies of p5, matter, three, chart, d3, katex
/evals           Golden set runner (Playwright + pipeline assertions)
/docs            All reference docs
```

## Commands

```
make dev          # docker-compose up: frontend :3000, backend :8000, postgres :5432
make test         # backend unit tests + frontend tests
make evals        # full golden-set pipeline run (costs tokens; confirm before running)
make migrate      # alembic upgrade head
make lint         # ruff + eslint + tsc --noEmit
```

## Conventions

- Python: ruff, type hints everywhere, pydantic models for all LLM I/O. Every LLM node validates its own output schema and retries once on parse failure.
- TypeScript: strict mode, zod at every boundary (SSE events, bridge messages, API responses).
- Prompts live in `/backend/prompts/*.md`, never inline in Python strings. Version them in git; note prompt changes in commit messages with prefix `prompt:`.
- Every LangGraph node logs input, output, model, tokens, latency to the trace table.
- Commit style: conventional commits. One logical change per commit.
- No em dashes in user-facing copy or docs.

## When editing the Generator or Verifier prompts

1. Run `make evals` before and after. Paste the delta into the PR description.
2. Never weaken a Verifier safety check to make an eval pass. Fix the Generator instead.
3. If a failure class repeats 3+ times, add a deterministic rule to `postprocess.py` rather than growing the prompt.

## Cost discipline

Log cost per pipeline run. If a single run exceeds the budget in `config.py`, fail loudly. During prompt tuning, prefer running evals on the 4-item smoke subset (`make evals-smoke`) before the full 12.

## Session start checklist

1. Read `docs/PLANNING.md`, find the current phase and next unchecked task.
2. Confirm the task with the user if scope is ambiguous.
3. Work the task, run tests, update the checklist in PLANNING.md in the same commit.
