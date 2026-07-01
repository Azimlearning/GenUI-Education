# Synapse — Local Dev Start Guide

> Refer back to this file whenever you want to spin up the app locally. Two servers, two terminals.

## Prerequisites (one-time)

- `uv` on PATH (Python 3.13 is provisioned automatically by `uv sync`).
- `bun` on PATH.
- `backend/.env` exists with at least one of `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` set (copy from `backend/.env.example` if missing). Without either key, agents fall back to scripted P0 behaviour — the app still runs.

## Start the backend

```powershell
cd Synapse\backend
uv run uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- First run (or after a dependency change) do `uv sync` first.
- Restart this process any time you change `.env` — env vars are only read at startup.

## Start the frontend

```powershell
cd Synapse\frontend
bun dev
```

- App: **http://localhost:3000** ← open this one
- First run (or after a dependency change) do `bun install` first.

## Troubleshooting

- **Runtime error `ENOENT ... .next/server/app/page.js`**: stale/corrupted `.next` build cache, usually from a previous dev server not shutting down cleanly. Stop the frontend process, delete `frontend/.next`, restart `bun dev`.
- **Only one dev server of each kind at a time** — running two `bun dev` (or two `uvicorn --reload`) instances against the same folder causes file-lock/build-cache conflicts.
- **uv not found / "not a valid application for this OS platform"**: reinstall via `irm https://astral.sh/uv/install.ps1 | iex` (PowerShell).
