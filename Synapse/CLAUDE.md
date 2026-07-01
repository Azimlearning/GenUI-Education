# Synapse — Claude Context

> Read this file at the start of every session, then check `refdocs/STATUS.md` for where we are, then skim `refdocs/synapse-prd.md`. Synapse is a **visible multi-agent pedagogical platform** for Malaysian KSSM SPM science (Form 4–5 Physics · Chemistry · Biology). A team of agents diagnoses a student, decides the pedagogically-correct move, and **composes an interactive learning experience from a pre-built component library** — streamed to the browser as Generative UI. The PRD is the source of truth — this file is the short operating brief. Keep it short.

---

## Order of authority (when docs conflict, surface it — don't resolve silently)

0. `refdocs/STATUS.md` — **where we are right now.** Phase checklist + current module's progress. Check this first, every session.
1. `refdocs/synapse-prd.md` — **what & why.** Owns scope, the 4 agents, the component library, architecture, provider strategy, roadmap, Decision Log.
2. `refdocs/concept-catalog.md` — **the 12 demo concepts → interaction patterns** (the build manifest, D-13). Mirrors `backend/app/components/registry.py`.
3. `refdocs/changelog/DECISIONS.md` — **settled calls.** Read before re-debating an architectural choice.
4. `refdocs/plans/*.md` — **what to build & why** (produced by the planning skill).
5. `refdocs/execution/*.md` — **how & in what order** (produced by the planning skill).
6. `refdocs/synapse-sources.md` — **raw research** (KSSM syllabus, misconception literature, GenUI references).

If two docs disagree, stop and ask. Don't pick one and move on.

---

## Mandatory rules

### 1. Update the changelog after every session
After any session that changed code, made a decision, or modified a plan, add an entry to **`refdocs/changelog/CHANGELOG.md`** (format is in that file). Do not skip. Even a one-line fix gets a one-line entry.

### 2. Plan before you build
Before implementing any non-trivial feature, a **plan doc** (`refdocs/plans/`) and an **execution doc** (`refdocs/execution/`) must exist. If they don't, create them (or run the planning skill) before writing code.

### 3. Log decisions as ADRs
New architectural/design decision → add an ADR to `refdocs/changelog/DECISIONS.md` (Decision → Why → Rejected/Trade-off). Mark unresolved assumptions `ASSUMED:` and surface them at the next checkpoint.

### 4. Keep docs current
If you deviate from a plan during execution, update the execution doc to match reality. Stale docs are worse than no docs.

---

## The hard constraints (these are mechanism, not preference)

1. **The agents SELECT and CONFIGURE; they never generate UI from scratch.** GenUI = intelligent selection + arrangement of pre-built, domain-correct components (D-01). The moat is the faithful KSSM component library, not raw generation. No hallucinated interactives.
2. **Components are parameterised by INTERACTION PATTERN, not by topic.** One "gradient/diffusion sandbox" serves osmosis, dialysis, gas exchange. ~12–18 patterns cover a large slice of the syllabus (D-02). Never build a bespoke component per topic.
3. **The agent reasoning must be VISIBLE.** The demo wow is watching Diagnostician → Strategist → Composer think out loud, live. Stream every agent step to the UI — never collapse the pipeline into a silent finished page (D-03). This is the thing Google's dynamic view structurally cannot show.
4. **All LLM calls go through the Provider Router.** Never call a provider SDK directly from an agent. Each agent has a config-driven primary + fallback chain in `backend/app/providers/config.py` (D-05). **Anthropic Claude is the live primary** (D-14) — Haiku for Diagnostician/Composer, Sonnet for Strategist; OpenAI is the fallback. Reorder/swap providers in config only.
5. **Keys are server-side only.** API keys live in `backend/.env`, used only from the Python backend — never in the Next.js client, never `NEXT_PUBLIC_`.
6. **Grounded, not improvised, diagnosis.** The Diagnostician reasons against an explicit, pre-authored KSSM misconception library (`backend/app/knowledge/`), not free improvisation (D-04). That grounding is the citable pedagogical-impact artifact.
7. **Demo scope = the 12 locked concepts, flagships-first (D-13).** Build all 12 (3 Chem · 3 Phys · 6 Bio → 14 patterns, see `concept-catalog.md`) as real interactives, but in flagship order (osmosis · bonding-electrons · forces-motion) so there is always a flawless fallback demo. Per-component faithfulness is non-negotiable (constraint #1) — a concept is "live" only when its science is correct. (This supersedes the old "1-subject-deep" cap; the depth discipline survives as the build order.)
8. **Two hackathons, one product.** Codex KL framing = Malaysian SPM user + B40 equity. hackAstone framing = agentic pedagogy + academic novelty. Same codebase; adapt the pitch, not the build (D-07).

---

## The four agents (the pipeline IS the product)

| Agent | Role | Reads | Writes |
|---|---|---|---|
| **Diagnostician** | Identify the student's specific conceptual state / misconception | question + learner profile + misconception library | a diagnosis (`misconception` \| `knowledge_gap` \| `mastery_check`) |
| **Pedagogy Strategist** | Pick the pedagogically-correct intervention (contrasting cases, predict-observe-explain, worked-example fading, retrieval practice) | diagnosis | a strategy + target interaction pattern |
| **Component Composer** | Select + configure a component from the library to enact the strategy | strategy + component registry | a typed component block (SSE) |
| **Tutor Loop** | Watch the interaction, update the persistent learner model, schedule spaced repetition | interaction events | learner-profile update |

Data flows **forward** (question → diagnosis → strategy → composed component) and the tutor loop closes it **back** (interaction → learner model → informs the next composition). See PRD §5.

---

## Stack (see DECISIONS ADR-008..012)

**Backend:** Python 3.13 · FastAPI · **LangGraph** (agent orchestration) · Pydantic v2 (typed agent state + component blocks) · SSE (`sse-starlette`) · provider abstraction over OpenAI / Anthropic / others · learner state store (SQLite for dev → Firebase for the hosted demo, D-11).

**Frontend:** Next.js (App Router) · TypeScript · Tailwind · the pre-built interactive **component library** (`frontend/components/library/`, organised by interaction pattern) · an SSE client that renders streamed typed component blocks · **bun**.

**Contract:** the backend streams **typed component blocks** (`{ pattern, props, meta }`) over SSE; the frontend maps `pattern` → a React component in the library and hydrates it with `props`. This block schema is the load-bearing seam between the two runtimes — keep `backend/app/models/schemas.py` and `frontend/lib/blocks.ts` in sync (D-10).

---

## Build sequence (PRD §9)

**P0** Foundation (this skeleton: monorepo, FastAPI shell, LangGraph graph with stub nodes, SSE contract, Next.js shell + landing, provider-router + registry + misconception stubs) → **P1** One live vertical slice (osmosis: real Diagnostician → Strategist → Composer stream → the live gradient/diffusion sandbox → Tutor Loop write) → **P2** Component library depth (2–3 patterns faithful) → **P3** Learner model + spaced repetition → **P4** Polish + demo script → **P5** Second-hackathon framing pass.

**Never build the second of anything until the first is green end-to-end.** One question → one diagnosis → one strategy → one composed component → one learner-model write, before scaling out.

---

## When blocked

- **Open question:** check PRD §11. If unresolved, write your assumption to `DECISIONS.md` as `ASSUMED:`, proceed, surface at the next checkpoint.
- **Doc conflict:** stop. Quote both passages and ask. Don't pick silently.
- **Ambiguous spec:** prefer the narrower-scope / more-faithful / more-visible-reasoning option. Log the choice.

---

*Companion brief to `refdocs/synapse-prd.md`. Last updated: 2026-07-01.*
