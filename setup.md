# Setup Guide

This repository's only runnable code is under [`Synapse/`](Synapse/) (a FastAPI backend + Next.js
frontend monorepo). Everything else at the repo root (`Codex hackathon/`, `Hackastone/`,
`phase0-research/`) is reference material — nothing to install or run there.

You need **two terminals**: one for the backend, one for the frontend.

---

## Prerequisites

| Tool | Used for | Install |
|---|---|---|
| [`uv`](https://docs.astral.sh/uv/) | Python package/venv manager (provisions Python 3.13 automatically) | `irm https://astral.sh/uv/install.ps1 \| iex` (PowerShell) or see uv docs |
| [`bun`](https://bun.sh/) | Frontend package manager + dev server | see bun docs |
| Anthropic and/or OpenAI API key | Live LLM-driven agents (optional) | see below |

You do **not** need an API key to run the app — without one, the agents fall back to scripted P0
behaviour and the demo still runs end-to-end. Set a key to switch on live Claude/GPT reasoning.

---

## 1. Clone and enter the project

```bash
git clone https://github.com/Azimlearning/GenUI-Education.git
cd GenUI-Education/Synapse
```

## 2. Backend setup

```bash
cd backend
uv sync                        # installs deps + provisions Python 3.13
cp .env.example .env           # then optionally fill in ANTHROPIC_API_KEY / OPENAI_API_KEY
uv run uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Run backend tests: `uv run pytest`
- Restart this process any time you edit `.env` — env vars are only read at startup.

### Backend environment variables (`backend/.env`)

| Variable | Required? | Notes |
|---|---|---|
| `FRONTEND_ORIGIN` | Yes (default provided) | CORS origin for the Next.js dev server, default `http://localhost:3000` |
| `ANTHROPIC_API_KEY` | Optional | Enables live Claude-driven agents (primary provider) |
| `OPENAI_API_KEY` | Optional | Fallback provider if Anthropic is unset/unavailable |
| `LEARNER_STORE` | Optional | `memory` (default, dev) or `sqlite` for local persistence |

## 3. Frontend setup

Open a second terminal:

```bash
cd Synapse/frontend
bun install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE=http://localhost:8000
bun dev
```

- App: **http://localhost:3000** ← open this one
- Teacher dashboard: http://localhost:3000/teacher

## 4. Try it

Ask a science question (or click a suggested scenario chip) and watch the four agents
(Diagnostician → Pedagogy Strategist → Component Composer → Tutor Loop) reason live, then a
science-faithful interactive renders from the component library.

---

## Troubleshooting

- **Runtime error `ENOENT ... .next/server/app/page.js`** — stale/corrupted `.next` build cache,
  usually from a previous dev server not shutting down cleanly. Stop the frontend process, delete
  `Synapse/frontend/.next`, restart `bun dev`.
- **Only one dev server of each kind at a time** — running two `bun dev` (or two
  `uvicorn --reload`) instances against the same folder causes file-lock/build-cache conflicts.
- **`uv` not found / "not a valid application for this OS platform"** — reinstall via
  `irm https://astral.sh/uv/install.ps1 | iex` (PowerShell).
- **Agents seem "scripted" / generic** — no API key is set in `backend/.env`; this is expected
  fallback behaviour. Add `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) and restart the backend.

For deeper architecture, provider-router, and agent details, see
[`Synapse/CLAUDE.md`](Synapse/CLAUDE.md) and [`Synapse/refdocs/synapse-prd.md`](Synapse/refdocs/synapse-prd.md).
