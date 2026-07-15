# TECHNICAL.md — Axiom Stack, Conventions, Setup

## 1. Stack (locked decisions)

| Layer | Choice | Version policy |
|---|---|---|
| Frontend | Next.js 14 App Router, TypeScript strict, Tailwind | pin minor |
| Backend | FastAPI, Python 3.11+, uvicorn | pin minor |
| Orchestration | LangGraph (Python) | pin exact |
| LLM SDK | anthropic (Python) | pin minor |
| DB | Postgres 16, SQLAlchemy 2.x, Alembic | pin major |
| Validation | pydantic v2 (backend), zod (frontend) | pin minor |
| Testing | pytest, Playwright, vitest | pin minor |
| Artifact runtime | iframe srcdoc, allow-scripts only | permanent |

Rejected alternatives, so nobody relitigates them: Sandpack/WebContainers (heavyweight, unnecessary for single-document artifacts), runtime JSX engines (JSX generation is less reliable than vanilla HTML/JS and adds a transpile layer), component-library fallback (violates Tier 3 principle), CDN script loading (breaks sandbox guarantees and offline evals).

## 2. Repository structure

```
axiom/
├── CLAUDE.md
├── docker-compose.yml
├── Makefile
├── docs/                      # this docs pack + super prompt
├── vendor/                    # pinned libs + CHECKSUMS.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # chat
│   │   ├── library/page.tsx
│   │   └── api/               # edge proxies only if needed; logic lives in backend
│   ├── components/
│   │   ├── chat/              # MessageList, Composer, StreamRenderer
│   │   └── artifact/          # ArtifactCard, SandboxFrame, ProgressStages,
│   │                          # DegradedCard, BridgeListener, RemixInput
│   ├── lib/
│   │   ├── sse.ts             # typed SSE client, zod schemas
│   │   └── bridge.ts          # postMessage validation
│   └── types/events.ts        # mirrors backend/schemas/events.py
├── backend/
│   ├── main.py
│   ├── config.py              # budgets, model ids, timeouts, rate limits
│   ├── api/                   # routers: ask, artifact, library, vendor
│   ├── graph/
│   │   ├── state.py
│   │   ├── build.py           # StateGraph assembly + conditional edges
│   │   └── nodes/             # router.py, explainer.py, planner.py,
│   │                          # generator.py, verifier.py, tutor.py, cache.py
│   ├── postprocess.py
│   ├── prompts/               # *.md, one per node, versioned header comment
│   ├── schemas/               # pydantic: Intent, ArtifactPlan, VerifierReport, events
│   ├── db/                    # models.py, session.py, migrations/
│   └── services/              # cache.py, traces.py, delivery.py (the gate)
└── evals/
    ├── golden.yaml            # 12 golden queries + assertions
    ├── hostile.yaml
    ├── run.py                 # pipeline runner + metrics
    └── render_check.py        # Playwright: axiom_ready, control wiring, forbidden APIs
```

## 3. Environment variables

```
ANTHROPIC_API_KEY=
DATABASE_URL=postgresql+asyncpg://...
MODEL_STRONG=            # generator, verifier, planner
MODEL_FAST=              # router, explainer, tutor
MAX_RUN_COST_USD=0.75    # hard per-run ceiling, fail loudly
ARTIFACT_TIMEOUT_S=30
GEN_RATE_LIMIT_PER_HOUR=10
```

Never commit real values. `.env.example` stays current in the same PR as any new variable.

## 4. Coding conventions

### Backend
- Async everywhere; no blocking calls inside graph nodes.
- Every LLM node: build prompt from `/prompts/*.md` + typed inputs, call model, parse into pydantic schema, one silent retry on parse failure, raise typed NodeError after that.
- No raw dict passing between nodes. State fields are typed.
- `services/delivery.py` owns the only path to `artifact_done`. See SECURITY.md section 4.
- postprocess.py rules are pure functions `str -> str | PostprocessReject`, each with a unit test and a comment citing the failure it fixes.

### Frontend
- All server data crosses a zod schema at the boundary. No `as` casts on network data.
- SSE client is a single reducer: events in, UI state out. No component subscribes to raw SSE.
- ArtifactCard is a state machine: `loading(stage) → ready | degraded | flagged`. Implement with a discriminated union, not booleans.
- No localStorage/sessionStorage anywhere in artifact-adjacent code paths.

### Prompts
- Each prompt file starts with a header: version, date, eval pass rate at last change.
- Examples in Block D of the generator prompt are the quality ceiling; edit them before adding instructions.
- Verifier prompt changes require re-running the hostile suite.

## 5. Vendored libraries

Pinned versions downloaded once into `/vendor` with recorded SHA-256 checksums (`vendor/CHECKSUMS.txt`, verified in CI). Served by FastAPI static route `/vendor/*` with long cache headers. The generator prompt references these exact paths. Adding a library requires: security review note in SECURITY.md, checksum entry, prompt Block C update, and an eval demonstrating need.

Initial set: p5.js, matter.js, three.js, chart.js, d3.js, katex (+katex.min.css).

## 6. Local development

```
git clone ... && cd axiom
cp .env.example .env      # fill ANTHROPIC_API_KEY
make dev                  # builds and starts all services
make migrate
open http://localhost:3000
```

`make dev` must work from a clean clone with only Docker and make installed. If it does not, fixing that is the highest-priority bug.

## 7. Testing strategy summary

- Unit: postprocess rules, cache key normalization, delivery gate type safety, SSE reducer.
- Integration: full graph runs with mocked LLM responses (recorded fixtures) so CI is deterministic and free.
- Live evals: `make evals` runs the golden set against real models; not in CI by default, run before merging prompt or node changes. `make evals-smoke` runs items 1, 4, 10, 12 only.
- Render checks: Playwright asserts axiom_ready, at least one wired control (dispatch input event, assert canvas/DOM mutation), zero forbidden API strings.

Full detail in EVALS.md.

## 8. Performance budgets

| Metric | Budget |
|---|---|
| First text token | < 2s p95 |
| Cache-hit artifact render | < 1s |
| Cache-miss artifact (no retry) | < 45s p95 |
| Artifact iframe memory | < 150MB (Playwright check) |
| Generated artifact size | < 200KB HTML (post-processor rejects larger) |
