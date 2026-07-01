# Changelog — Synapse

> One entry per session that changed code, made a decision, or modified a plan. Newest first.
> Format: `## YYYY-MM-DD — title` then bullet points. Even a one-line fix gets a one-line entry (CLAUDE.md rule 1).

---

## 2026-07-01 — Demo scope locked (12 concepts), Anthropic primary, name/layout settled

- **Scope (D-13 / ADR-013):** locked the **12 demo concepts** the team chose (3 Chemistry, 3 Physics, 6 Biology) and mapped them to **14 interaction patterns**. This supersedes the "1-subject-deep" cap (D-06/ADR-005); the depth discipline is preserved as a **flagships-first build order** (osmosis · bonding-electrons · forces-motion). New authoritative build manifest: `refdocs/concept-catalog.md`.
- **Registry:** rewrote `backend/app/components/registry.py` — all 14 patterns (with prop schemas) + a `CONCEPTS` catalog (the 12 concepts → pattern + experiment + chatbot idea). Added `get_concept` / `concepts_for_subject`. Folded `titration-sandbox` into `reaction-lab-sandbox`; dropped `contrasting-pair-walkthrough` in favour of `electron-bonding-explorer` for bonding. `pytest` still 2/2; all concept→pattern references validated.
- **Provider (D-14 / ADR-014):** **Anthropic Claude** is now the live primary in the router (Haiku for Diagnostician/Composer, Sonnet for Strategist), OpenAI the fallback. Implemented the Anthropic adapter in `providers/router.py` (lazy `import anthropic`, degrades to scripted if SDK/key absent). Reordered `providers/config.py`; added `anthropic` to `pyproject.toml`. Agents remain scripted until P1 flips them to call the router.
- **Name / layout (D-15 / ADR-015):** reviewed the UI/UX team's `uiux_team/EDUNOVA/` "TutorLah!" sidebar prototype. Kept the name **Synapse** and the **centered** layout; recorded the decision and salvaged the per-subject colour-theming idea. No frontend layout change.
- Docs updated: PRD §6/§9/§10/§11, DECISIONS (ADR-005 superseded; +ADR-013/014/015), sources, STATUS, and the new `concept-catalog.md`.
- Produced the one-shot build **superprompt**: `refdocs/SUPERPROMPT.md`.

## 2026-07-01 — P0 skeleton scaffolded

- Created the monorepo skeleton for Synapse under `Genui/Synapse/` per the confirmed decisions: **Python (FastAPI + LangGraph) backend + Next.js frontend**, joined by an **SSE typed-component-block contract**, with a **config-driven multi-provider router (no hard default)**, and depth = **runnable shell + structure + docs**.
- Ported the documentation/workflow system from the OmniX reference the user likes: `CLAUDE.md` operating brief + `refdocs/` (PRD as source of truth, `STATUS.md`, `synapse-sources.md`, `changelog/{CHANGELOG,DECISIONS}.md`, `plans/`, `execution/`).
- Backend: FastAPI app (`app/main.py`), Pydantic v2 SSE schemas (`app/models/schemas.py`), LangGraph `StateGraph` wiring the 4 agents as scripted stubs (`app/agents/`), provider router + config (`app/providers/`), component registry with the 6 seed patterns (`app/components/registry.py`), seed KSSM misconception KB (`app/knowledge/misconceptions.py`), in-memory learner store behind an interface (`app/store/`), and the `POST /api/ask` SSE route (`app/api/routes.py`).
- Frontend: Next.js App Router shell, `globals.css` with the Synapse indigo/teal tokens ported from `Synapse_Demo.html`, landing page matching the demo identity (topbar + logo mark + hero + prompt card + scenario chips), SSE client + block-schema mirror (`lib/`), the visible `AgentPipeline` panel, and a `library/` of one placeholder component per seed pattern behind a `BlockRenderer`.
- Recorded ADR-001..012 in `DECISIONS.md` and D-01..D-12 in the PRD Decision Log.
- **Verified end-to-end this session:** backend `pytest` 2/2 pass; booted uvicorn and confirmed a live `POST /api/ask` streams all 4 agents' `agent_step`s + the osmosis `component_block` + the tutor-loop write + `done` over SSE. Frontend `bunx tsc --noEmit` clean and `bun run build` clean (4 routes). The Python↔Next SSE seam (D-10) is proven working, not just typed.
- **Deliberately deferred to P1:** agent nodes are scripted (no LLM); no provider adapter wired to a real SDK; learner store in-memory only.
- Bootstrap plan + execution docs created: `plans/2026-07-01-p0-foundation.md`, `execution/2026-07-01-p0-foundation.md`.
