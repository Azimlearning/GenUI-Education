# Changelog — Synapse

> One entry per session that changed code, made a decision, or modified a plan. Newest first.
> Format: `## YYYY-MM-DD — title` then bullet points. Even a one-line fix gets a one-line entry (CLAUDE.md rule 1).

---

## 2026-07-01 — P4 polish + hackAstone deliverables (teacher view, grounded pedagogy, docs)

- **P4 polish.** Per-subject accent theming (Bio green, Chem sand, Physics blue) keyed off the composed block's subject (D-15), applied as a subtle header tint in `PatternCard`. Added the "How Synapse is different" explainer to the landing page (Innovation dimension). Refreshed the footnote/chips.
- **Teacher view (commercial wedge).** New `/teacher` Next.js page + `GET /api/teacher` showing every learner's mastery, misconceptions, and what's due for review. Added `student_ids()` to the store interface (both impls).
- **Grounded pedagogy (Educational Significance).** Expanded the misconception KB with real sourced citations (Odom & Barrow, Taber, Clement + Halloun-Hestenes) and two new entries (photosynthesis-food-from-soil with Driver; current-used-up with Shipstone). Added `electricity` alias to the circuit pattern so the new entry routes.
- **Deploy config (TRL), not deployed.** Backend `Dockerfile` + `.dockerignore` (uv, Python 3.13, SQLite store), frontend `vercel.json`. Host selection parked for the owner (decisions.md P-a).
- **Submission deliverables written:** `refdocs/GO-TO-MARKET.md`, `refdocs/EVALUATION-PLAN.md`, `refdocs/VIDEO-SCRIPT.md` (≤8-min shot-by-shot, osmosis "aha" marked as the hook), `refdocs/PROJECT-DESCRIPTION.md` (explicitly answers all four judging dimensions + Responsible AI). Updated `README.md` (30-second what-it-is, live-URL placeholder, teacher view, run instructions).
- **Verified:** `pytest` 12/12, `tsc` clean, `next build` clean (5 routes incl. `/teacher`), flagship + new-misconception routes confirmed.

## 2026-07-01 — P3: the learner loop closes

- **Interaction events flow back.** The three flagship components report how the learner did via a new `onInteraction` callback (threaded page → BlockRenderer → component), which POSTs to `POST /api/interaction` with the topic + misconception from the block meta.
- **Mastery + spaced repetition (Tutor Loop).** `record_interaction` moves mastery toward 1 on a correct attempt and decays it on a wrong one; a correct attempt on a diagnosed misconception marks it resolved and pushes the next review out (7 days), a wrong one resurfaces it (1 day). `due_for_review()` surfaces what's overdue.
- **The next composition is informed by history.** The Diagnostician reads the learner profile: a previously-cleared misconception flips the diagnosis to a mastery check (so we don't re-teach); an unresolved repeat adds a "resurfacing" step.
- **Profile surface.** `GET /api/profile/{id}` returns mastery + misconceptions + due-now; the landing page renders a "Your progress" panel (mastery bars, tracked misconceptions with cleared/in-review chips).
- **Verified live:** a correct osmosis interaction raised mastery to 0.34, marked the misconception resolved, pushed review to 7 days out; re-asking flipped the diagnosis to a mastery check. `pytest` 12/12 (+3 P3), `tsc` + `next build` clean.

## 2026-07-01 — P2: all 12 concepts render as real interactives, 3 flagships faithful

- **Two more faithful flagships.** `force-motion-sim` (trolley obeys ΣF = ma with kinetic friction; live velocity–time graph derived from the sim; targets the newton-force-to-keep-moving misconception) and `electron-bonding-explorer` (contrasting cases: metal + non-metal transfers → ionic, non-metal + non-metal shares → covalent; classification encoded in the component). Both predict-observe-explain.
- **Breadth: the remaining 9 patterns are now real, interactive components** (lighter-but-correct per the D-13 allowance): `process-timeline` (28-day cycle, ovulation ~day 14, hormone tracks), `stage-sequencer` (order mitosis stages), `matching-pairs` (enzyme↔substrate), `punnett-square-builder` (monohybrid 3:1), `signal-pathway-sim` (reflex arc), `atomic-structure-explorer` (Bohr shells 2,8,8), `circuit-builder-sandbox` (V=IR, series/parallel), `wave-optics-sandbox` (Snell's-law refraction + TIR), `reaction-lab-sandbox` (encoded reaction rules). Upgraded `quick-check-quiz` (mcq/numeric/coefficients with instant feedback) and `labelled-diagram-explorer` (digestive-tract journey).
- **Seam fully synced (D-10).** `frontend/lib/blocks.ts` now maps all 14 registry patterns to components; removed the two stale placeholders (`ContrastingPairWalkthrough`, `TitrationSandbox`). Composer gained scripted presets for the new flagships. Landing page: added a Physics scenario chip; footnote reflects live/scripted reality.
- **Verified:** `tsc` clean, `next build` clean (`/` 14 kB), `pytest` 9/9, and the three flagship routes confirmed end to end (osmosis → gradient-diffusion-sandbox, forces → force-motion-sim, bonding → electron-bonding-explorer).

## 2026-07-01 — P1: osmosis vertical slice is genuinely live end-to-end

- **Agents flipped to LLM-driven, scripted fallback kept.** `diagnostician` / `pedagogy_strategist` / `component_composer` now call the provider router when a key is configured, and fall back to their P0 scripted logic otherwise (`router.any_live()` gate → try → `except` → scripted). Diagnosis is **grounded**: the Diagnostician is handed the KB's candidate misconceptions and its `misconception_id` is validated against the KB (rejected if unknown, D-04). The Strategist's `target_pattern` is validated against `REGISTRY`.
- **Structured output via the router.** Added `ProviderRouter.run_structured()` — asks the model for a single JSON object, extracts it (fences/prose tolerant `_extract_json`), and **repairs once** on malformed output before giving up. Chosen over the SDK's native `output_config` to stay robust across `anthropic` SDK versions and to share one code path with the OpenAI fallback (see DECISIONS ADR-016).
- **OpenAI fallback adapter implemented** (`_call_openai`, lazy import) — activates only if `OPENAI_API_KEY` is set. Anthropic stays primary (D-14).
- **Faithfulness gate in code (constraint #6).** The Composer merges `_FAITHFUL_PINS` over the model's props, so `gradient-diffusion-sandbox` always ships `correct_direction: toward-higher-solute` / `particle: water` / `membrane: selectively-permeable` — a wrong model answer can't ship wrong science.
- **Observability (TRL signal).** New `providers/metrics.py` records provider/model/tokens/cost/latency per LLM call; exposed at `GET /api/metrics` for the dev panel.
- **Faithful flagship component.** Rewrote `frontend/components/library/GradientDiffusionSandbox.tsx` into a real predict-observe-explain sim: student commits a prediction → water animates across the membrane toward the higher-solute side → the misconception fails visibly → grounded explanation. Beaker + plant-cell (turgor/plasmolysis) modes; science encoded, not faked.
- **SQLite learner store (P1e).** Added `SqliteLearnerStore` behind the same `LearnerStore` interface; selected via `LEARNER_STORE=sqlite` (path `LEARNER_STORE_PATH`). `record_misconception` promoted to the interface; Tutor Loop no longer type-checks the concrete store.
- **Verified end-to-end this session (on abdul's machine):** backend `pytest` **9/9** (2 P0 + 7 new P1 covering JSON extraction/repair, the faithfulness gate, SSE serialisation, SQLite persistence + spaced-repetition scheduling, cost estimation); frontend `bunx tsc --noEmit` clean + `bun run build` clean (`/` 6.21 kB); a live `POST /api/ask` on uvicorn streamed all 4 agents + the faithful osmosis block + tutor-loop write + `done`. Runs with **no API key** (scripted); add `ANTHROPIC_API_KEY` to `backend/.env` for live Claude.
- New tracking files at `Synapse/`: `project-state.md` (running feature log) and `decisions.md` (pushed-back/minor decisions), per the build owner's request.

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
