# Synapse, pushed-back decisions (things I decided or deferred so we keep moving)

> Per your "make a decision, push back the minor stuff" instruction. Each entry is either a
> call I made to avoid stopping, or something genuinely parked for you to confirm later.
> Architectural ADRs still live in `refdocs/changelog/DECISIONS.md`; this file is the
> lightweight "we'll sort it later" list.

Last updated: 2026-07-01

## Decided (to keep moving), flag if you disagree

- **D-a, Frontend package manager is bun.** The project standardised on bun (bun.lock). It was
  missing on this machine, so I installed it via `npm i -g bun`. If you'd rather use plain npm,
  say so; the app builds under either.
- **D-b, Python is uv-managed 3.13.** The machine has 3.12; the backend needs 3.13 or newer.
  `uv sync` provisions its own 3.13 automatically, so no manual Python install is needed.
- **D-c, Run without keys by default.** With no `ANTHROPIC_API_KEY`, the agents fall back to the
  scripted P0 logic (by design, D-14). The demo still runs. Live Claude turns on the moment a key
  is in `backend/.env`. I did not hardcode or ask you for a key.
- **D-d, OpenAI fallback stays config-only for now.** The router has a real OpenAI adapter, but it
  only activates if `OPENAI_API_KEY` is set. Not required for the demo.
- **D-e, Structured output via prompt-and-parse, not the SDK's native structured-outputs.** Keeps
  one code path for both providers and avoids depending on a specific anthropic SDK version. Full
  reasoning is ADR-016 in `refdocs/changelog/DECISIONS.md`.

## Parked (need you eventually, not blocking the build)

- **P-a, Deploy target.** hackAstone TRL rewards a live URL. Frontend to Vercel is easiest; the
  FastAPI backend needs a host (Vercel functions / Render / Railway / Fly). I'll build the deploy
  config (Dockerfile plus vercel.json) but not deploy, since deploying needs your accounts. Pick a
  backend host when you're ready.
- **P-b, Firebase learner store (D-11).** For a hosted multi-device demo. I'm shipping SQLite now
  (local, zero setup). Firebase only matters once we deploy; it needs your Firebase project.
- **P-c, Real API key for the live demo plus video.** Needed before recording the video with live
  agent reasoning. The scripted fallback is fine for building and testing.
- **P-d, Science pressure-test.** Highest-value human step: a bio/physics/chem person should
  sanity-check each flagship sim before the video. Not a code task.
