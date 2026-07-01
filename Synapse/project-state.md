# Synapse, Project State (running build log)

> Laid-back build tracker. Updated as features land so you can see, at a glance, what
> actually works right now. The formal phase checklist lives in `refdocs/STATUS.md`; this file
> is the plain-language "what's done" view. Pushed-back decisions live in `decisions.md`.

Last updated: 2026-07-01

## TL;DR, where we are

**P1 is green.** The osmosis vertical slice is genuinely live end to end. All four agents run,
the first faithful interactive (the osmosis sim) is built, and the learner write persists to
SQLite. Next up: P2 flagships (bonding-electrons, forces-motion).

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

## Next (P2, remaining concepts, flagships first)

- [ ] `electron-bonding-explorer` (Chem flagship): ionic transfer vs covalent share.
- [ ] `force-motion-sim` (Phys flagship): ticker-tape trolley plus linked v-t graph.
- [ ] Then Tier 2/3 concepts from `refdocs/concept-catalog.md`.
- [ ] For each: registry entry, sourced misconceptions, faithful component, composer can emit it,
      browser-verify the science.

## Later

- P3, learner loop closes (interaction events update mastery plus spaced repetition).
- P4, polish, latency, subject theming.
- hackAstone Part B (teacher view, grounded pedagogy, go-to-market, evaluation plan).
- hackAstone Part C (video script, project description, README live URL).

## How to run right now

Backend: `cd backend` then `uv run uvicorn app.main:app --reload --port 8000`
Frontend: `cd frontend` then `bun install` then `bun dev` then open http://localhost:3000

To use live Claude instead of the scripted fallback: copy `backend/.env.example` to
`backend/.env` and set `ANTHROPIC_API_KEY`.
