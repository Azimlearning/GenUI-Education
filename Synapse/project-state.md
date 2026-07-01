# Synapse, Project State (running build log)

> Laid-back build tracker. Updated as features land so you can see, at a glance, what
> actually works right now. The formal phase checklist lives in `refdocs/STATUS.md`; this file
> is the plain-language "what's done" view. Pushed-back decisions live in `decisions.md`.

Last updated: 2026-07-01

## TL;DR, where we are

**P1 through P4 are green, and the hackAstone deliverables are largely done.** The pipeline is
live end to end, all 12 concepts render as real interactives (3 flagships faithful), the learner
loop closes, there is a teacher dashboard, the misconception KB has real citations, deploy config
is built (not deployed), and the written submission docs are drafted (go-to-market, evaluation,
video script, project description, README). What's left is mostly on you: add an API key, pick a
deploy host, record the video, and have a subject teacher pressure-test the sims.

Runs today with **no API key** (agents fall back to scripted behaviour). Add `ANTHROPIC_API_KEY`
to `backend/.env` to switch the agents to live Claude.

## Done

- [x] Repo cloned to this machine, on `main`.
- [x] P0 skeleton read and understood (backend and frontend seam).
- [x] Toolchain checked: Python 3.12 plus uv (uv provisions 3.13), node 24, bun installed via npm.
- [x] Model IDs confirmed against the claude-api skill (Haiku 4.5 and Sonnet 5, both valid).
- [x] Tracking files created (`project-state.md`, `decisions.md`).
- [x] **P1a** Provider router: `run_structured()` (JSON extract plus one repair pass), OpenAI
      fallback adapter, per-call spend/latency logging (`providers/metrics.py`, `GET /api/metrics`).
- [x] **P1b** Agents flipped to LLM-driven with scripted fallback. Diagnosis grounded in the KB
      (misconception_id validated); Strategist target_pattern validated against the registry.
- [x] **P1c** Faithful `gradient-diffusion-sandbox` React component (predict, run, water moves to
      the higher-solute side, misconception fails visibly, grounded explanation). Beaker plus
      plant-cell (turgor/plasmolysis) modes.
- [x] **P1 gate** Faithfulness pinned in code (osmosis `correct_direction` always correct).
- [x] **P1e** SQLite learner store behind the same interface (`LEARNER_STORE=sqlite`).
- [x] **P1 verify** pytest 9/9, tsc clean, next build clean, live POST /api/ask streamed the
      full sequence (4 agents plus faithful block plus tutor write plus done).

## Done (P2, all concepts render as real interactives)

- [x] `electron-bonding-explorer` (Chem flagship): ionic transfer vs covalent share, contrasting cases.
- [x] `force-motion-sim` (Phys flagship): trolley obeys F=ma plus a live v-t graph.
- [x] The other 9 patterns built as lighter-but-correct interactives; quiz + digestive upgraded.
- [x] Seam fully synced: all 14 patterns map to components in `lib/blocks.ts`.

## Done (P3, learner loop closes)

- [x] Components post interaction events; Tutor Loop updates mastery plus spaced repetition.
- [x] Diagnostician reads history: a cleared misconception flips the next visit to a mastery check.
- [x] `GET /api/profile/{id}` plus an on-screen "Your progress" panel.

## Done (P4 + hackAstone deliverables)

- [x] Subject accent theming; "How Synapse is different" explainer.
- [x] Teacher dashboard (`/teacher` + `GET /api/teacher`).
- [x] Misconception KB expanded with real sourced citations (+2 new entries).
- [x] Deploy config built (backend Dockerfile, frontend vercel.json), not deployed.
- [x] Written deliverables: GO-TO-MARKET, EVALUATION-PLAN, VIDEO-SCRIPT, PROJECT-DESCRIPTION; README refreshed.

## Left for you (not code)

- [ ] Add `ANTHROPIC_API_KEY` to `backend/.env` for a live demo and the video.
- [ ] Pick a backend deploy host (Render/Railway/Fly/Vercel functions); frontend to Vercel.
- [ ] Record the 8-minute video (script in `refdocs/VIDEO-SCRIPT.md`).
- [ ] Have a bio/physics/chem teacher pressure-test each flagship sim's science.

## Possible next code work (optional)

- [ ] Bahasa Malaysia interface toggle for the flagship flows.
- [ ] Accessibility pass (aria labels, focus states) and an offline-capable build.
- [ ] Firebase learner store for a hosted multi-device demo (D-11).
- hackAstone Part B (teacher view, grounded pedagogy, go-to-market, evaluation plan).
- hackAstone Part C (video script, project description, README live URL).

## How to run right now

Backend: `cd backend` then `uv run uvicorn app.main:app --reload --port 8000`
Frontend: `cd frontend` then `bun install` then `bun dev` then open http://localhost:3000

To use live Claude instead of the scripted fallback: copy `backend/.env.example` to
`backend/.env` and set `ANTHROPIC_API_KEY`.
