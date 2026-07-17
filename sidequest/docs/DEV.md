# DEV.md, Running Axiom Locally

Two supported paths. Path A (no Docker) is what works on this dev machine today
and is the fastest way to a running app. Path B is the canonical docker-compose
setup from TECHNICAL.md, for machines that have Docker.

## Prerequisites

- Python 3.11+ (3.13 works)
- Node 20+ (24 works)
- An Anthropic API key (optional: without one the app runs in echo mode, which
  streams the plumbing but makes no model calls and builds no artifacts)

## 0. Configure

From the repo root (`sidequest/`):

```
cp .env.example .env
```

Edit `.env` and set:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Everything else can stay at its default. Backend defaults to port 8000,
frontend to 3000, and they are pre-wired to find each other there.

## Path A: no Docker (venv + npm)

### 1. Backend (terminal 1)

```
cd backend
python -m venv .venv                       # first time only
.venv\Scripts\pip install -r requirements-dev.txt    # first time only
.venv\Scripts\python -m uvicorn main:app --port 8000 --reload
```

Sanity check in a browser or another terminal:

```
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok","llm":"live"}`. If it says `"llm":"echo"`, the API
key was not picked up; check `.env` is at the repo root, then restart.

### 2. Frontend (terminal 2)

```
cd frontend
npm install          # first time only
npm run dev
```

Open http://localhost:3000 and ask a question. See `docs/PROMPT_TESTS.md` for
what to ask and what should happen.

### 3. About Postgres (optional in Path A)

Chat and artifact generation work WITHOUT a database. Persistence (sessions,
messages, trace rows) is fire-and-forget: with no Postgres you will see
`trace write failed` / `save_message failed` errors in the backend log. They
are loud on purpose and harmless to the stream.

If you want real persistence without Docker, point `DATABASE_URL` in `.env`
at any Postgres 16 you have, then:

```
cd backend
.venv\Scripts\alembic upgrade head
```

## Path B: Docker (canonical)

```
make dev        # builds and starts frontend :3000, backend :8000, postgres :5432
make migrate    # creates the schema (first run)
```

`make dev` must work from a clean clone with only Docker and make installed;
if it does not, that is a priority bug (TECHNICAL.md section 6).

## Tests and lint

```
# backend (from backend/)
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ruff check .

# frontend (from frontend/)
npm run test         # vitest
npm run typecheck    # tsc --noEmit
npm run lint         # eslint

# vendored library integrity (from repo root)
python vendor/verify.py
```

## Evals (cost real tokens, backend must be running)

First-time setup for the render checks:

```
backend\.venv\Scripts\pip install -r evals/requirements.txt
backend\.venv\Scripts\python -m playwright install chromium
```

Then:

```
cd evals
..\backend\.venv\Scripts\python run.py --smoke --render     # G1,G4,G10,G12  (~$1-2)
..\backend\.venv\Scripts\python run.py --render             # all 12         (~$5-15)
..\backend\.venv\Scripts\python run.py --only G2 --render   # one item
..\backend\.venv\Scripts\python ui_smoke.py --query "why does ice float?" --expect-artifact
```

Results append to `evals/history.jsonl`.

## Timing expectations (measured, not aspirational)

| Thing | Typical |
|---|---|
| First streamed text | 2 to 3 s |
| Progress card appears | under 2 s |
| Artifact delivered | 1.5 to 4 min (provider first-token variance dominates; the staged card and the code preview are the wait experience) |
| Artifact after a verifier-forced revision | add another 1 to 2 min |
| text_only answers | done in ~10 s |

Rough cost per query: text-only about $0.01; an artifact $0.15 to $0.40
(planner + generator + verifier on the strong model); a revision adds
$0.10 to $0.25. Per-run ceiling is `MAX_RUN_COST_USD` (default 0.75), and the
run fails loudly past it.

## Troubleshooting

- **Port already in use.** Something is still listening on 8000 or 3000. On
  Windows PowerShell:
  `Get-NetTCPConnection -LocalPort 8000 -State Listen | % { Stop-Process -Id $_.OwningProcess -Force }`
- **Artifact stuck on "building the interactive" for minutes.** Usually
  provider time-to-first-token variance, not a hang; watch the backend log for
  the httpx 200 line. The branch gives up honestly at `ARTIFACT_TIMEOUT_S`
  (default 420 s) and shows a retry button.
- **Artifact failed with "didn't pass the science check".** Working as
  designed: the Verifier rejected all attempts. Hit Try again; a fresh plan
  usually lands.
- **CORS errors in the browser console.** You changed a port. Set
  `CORS_ORIGINS=["http://localhost:<your-frontend-port>"]` in `.env` and
  `NEXT_PUBLIC_API_BASE=http://localhost:<your-backend-port>` for the
  frontend, then restart both.
- **`"llm":"echo"` in /api/health.** No key found. The `.env` must sit at the
  repo root (next to docker-compose.yml), not inside backend/.
- **Vendored libs 404 inside artifacts.** Confirm `curl
  http://localhost:3000/vendor/p5.min.js` returns 200 (the frontend proxies
  /vendor to the backend); run `python vendor/verify.py`.

## Stopping

Ctrl+C in each terminal. For stray background servers, see the port-busy
command above (ports 8000 and 3000).
