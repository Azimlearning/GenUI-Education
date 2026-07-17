# Axiom

Ask a science question, get a verified, interactive explanation. Axiom streams a
text answer immediately and generates a working simulation, explorable diagram,
virtual experiment, or visualization at request time as self-contained HTML/JS,
rendered in a sandboxed iframe. There is no predefined component library for the
learning artifacts: every artifact is generated, verified, then shown.

## Status

**Phases 0-3 built and live-validated.** Type a science question: text streams
in about 2.5s while the artifact branch plans, generates, adversarially
verifies (with revision retries), post-processes, and delivers an interactive
artifact into the sandboxed iframe, with staged progress and a live code
preview masking the generation time. Unverified artifacts structurally cannot
reach the client (the delivery gate requires a type only the verifier can
mint). Next: Phase 4 (cache + library).

Current phase and the full task list: `docs/PLANNING.md`.

## Quick start

```
cp .env.example .env      # add ANTHROPIC_API_KEY (optional: see echo mode)
make dev                  # frontend :3000, backend :8000, postgres :5432
make migrate              # create the schema
```

Open http://localhost:3000 and ask something.

Without an `ANTHROPIC_API_KEY` the backend runs in **echo mode**: the pipeline
and the whole SSE path work end to end, but the Explainer echoes your question
instead of calling a model. A clean clone boots and streams without a key.

## Commands

```
make dev          # docker-compose: everything, hot reload
make test         # backend pytest + frontend vitest
make lint         # ruff + eslint + tsc --noEmit
make migrate      # alembic upgrade head
make evals        # full golden-set run; costs tokens (Phase 1)
```

## Layout

```
frontend/    Next.js 14 App Router, TypeScript, Tailwind
backend/     FastAPI, LangGraph pipeline, SQLAlchemy, Alembic
  prompts/   one markdown prompt per node, versioned, loaded at runtime
  graph/     StateGraph assembly and nodes
vendor/      pinned local copies of p5, matter, three, chart, d3, katex
evals/       golden and hostile suites
docs/        architecture, API, data model, security, evals, planning
```

## Reading order

1. `docs/super-prompt-tier3-science-app.md`: the founding brief and the why.
2. `docs/SYSTEM_ARCHITECTURE.md`: components, the two-branch request flow, the delivery gate.
3. `docs/API_SPEC.md`: SSE protocol and the iframe bridge contract.
4. `CLAUDE.md`: the rules that govern changes to this repo.

## The non-negotiables

Generated code never reaches a user unverified. The artifact iframe is
`sandbox="allow-scripts"` only, never `allow-same-origin`. Libraries are served
from `/vendor/` on our own origin, never a runtime CDN. Full threat model in
`docs/SECURITY.md`.
