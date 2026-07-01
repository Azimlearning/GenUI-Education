# Architectural Decisions — Synapse

> Record decisions here so they aren't re-debated in future sessions.
> Format: **Decision** → **Why** → **Trade-offs / what was rejected**.
> Canonical short list lives in `refdocs/synapse-prd.md` §10; this file expands the load-bearing ones.

---

## Product & Scope

### ADR-001 — Agents select and configure; they never generate UI from scratch (D-01)
**Decision:** The pipeline chooses a pre-built component and sets its parameters. It does not synthesise novel UI at runtime.
**Why:** This is what GenUI actually is (intelligent selection + arrangement of existing components), and it is the honest, defensible architecture. The moat is a faithful, domain-correct KSSM component library — not raw generation, where a general-purpose model out-resources us. Also eliminates hallucinated interactives.
**Rejected:** Free-form runtime UI generation — competes with Google on rendering (a losing game) and risks incorrect science.

### ADR-002 — Component library parameterised by interaction pattern, not topic (D-02)
**Decision:** One component per *interaction pattern*; topics are configurations of a pattern. `gradient-diffusion-sandbox` serves osmosis, dialysis, gas exchange, active transport.
**Why:** ~12–18 patterns then cover a large slice of Form 4–5 Phy/Chem/Bio. Keeps scope sane and is itself a strong pitch point.
**Rejected:** One bespoke component per topic — combinatorial explosion, unshippable.

### ADR-003 — Visible agent reasoning is the product (D-03)
**Decision:** Stream every agent step to the UI; render the pipeline thinking live.
**Why:** The demo wow — and the thing general-purpose GenUI structurally hides — is watching Diagnostician → Strategist → Composer reason. It is also exactly where the team's agent-orchestration muscle shows.
**Rejected:** Collapsing the pipeline into a silent finished page (Google's move) — throws away the differentiator.

### ADR-004 — Diagnosis grounded in a pre-authored misconception library (D-04)
**Decision:** The Diagnostician matches against an explicit KSSM misconception KB, not free improvisation.
**Why:** Grounded diagnosis reasons far better and is a citable pedagogical-impact artifact (scores Educational Significance). 
**Rejected:** Fully improvised diagnosis — weaker, unauditable, harder to defend to a subject-expert judge.

### ADR-005 — Brutally narrow demo scope; full syllabus is vision only (D-06) — SUPERSEDED by ADR-013
**Decision (original):** Build one subject deep, 2–3 killer components — flawless. Full syllabus in the doc only.
**Why:** A judge remembers one flawless "aha"; forgets five half-built demos.
**Superseded (2026-07-01):** the team chose breadth — all 12 concepts as real interactives (ADR-013). The *discipline* ADR-005 protected (depth over half-built breadth) is preserved as a **flagships-first build order**, not as a scope cap.

### ADR-013 — Demo covers all 12 locked concepts, flagships-first (D-13)
**Decision:** Build all 12 concepts the team locked — 3 Chemistry (reactions lab, bonding & electrons, atomic structure), 3 Physics (forces & motion, electricity, waves & optics), 6 Biology (menstrual cycle, osmosis, cell division, digestive system, genetics, neuron) — as real interactives, mapped to 14 interaction patterns (`concept-catalog.md`). Build order is flagships-first: osmosis · bonding-electrons · forces-motion.
**Why:** The team wants range across all three subjects for the demo; a broad, working library is a stronger commercial/scalability story (hackAstone commercial-viability + Codex marketability criteria) than one subject.
**Rejected:** 1-subject-deep (ADR-005, the safe option) — the team explicitly accepted the breadth risk. **Trade-off / mitigation:** 12 faithful sims is a lot for one sprint → flagships-first guarantees a flawless fallback demo; per-component faithfulness (constraint #1) is still required before a concept is "live"; long-tail concepts may ship as lighter-but-correct versions.

### ADR-015 — Product name Synapse; centered layout; TutorLah! sidebar superseded (D-15)
**Decision:** The product is **Synapse**; the frontend keeps the **centered** `Synapse_Demo.html` layout (prompt → visible agent pipeline → composed component). The UI/UX team's `uiux_team/EDUNOVA/` "TutorLah!" sidebar-chat prototype is not adopted.
**Why:** "Synapse" is the name in the hackathon context + the built skeleton; the centered layout foregrounds the visible-reasoning differentiator (D-03) directly under the question. Confirmed by the user.
**Rejected:** "TutorLah!"/"EDUNOVA" names; the sidebar-chat + visualizer-panel layout. **Salvaged:** the team's per-subject colour theming (Bio green, Chem sand, Physics blue) — fold in as a subtle subject accent in the centered layout.

### ADR-006 — One codebase, two hackathon framings (D-07)
**Decision:** Same product/codebase; adapt the *pitch* per hackathon (Codex KL = Malaysian SPM user + B40 equity; hackAstone = agentic pedagogy + academic novelty).
**Why:** Both are independent submissions of the same real work; the differentiators each rewards are already present.
**Rejected:** Forking the build per hackathon — wasteful, no benefit.

---

## Architecture

### ADR-008 — Monorepo: Python (FastAPI + LangGraph) backend + Next.js frontend (D-08)
**Decision:** Two runtimes in one repo (`backend/`, `frontend/`), joined by an SSE contract.
**Why:** LangGraph's canonical, richest ecosystem is Python, and the team's agent muscle is in Python; Next.js gives the interactive component library the frontend it needs. Confirmed by the user over the all-TypeScript alternative.
**Rejected:** All-TypeScript (Next.js + LangGraph.js) — one language/deploy, but weaker agent ecosystem for the team's strength. Python-only server-rendered — weakest for interactive GenUI. **Trade-off accepted:** two runtimes to wire and deploy; mitigated by keeping the seam a single small SSE contract.

### ADR-009 — Frontend owns component implementations; backend owns the registry (D-09)
**Decision:** React components live in `frontend/components/library/`; the backend holds only a *registry* (pattern id + prop schema + which topics/strategies it serves) that the Composer selects from.
**Why:** The Composer needs to *reason about* what's available (data), not import React. Clean separation; the registry is small and language-neutral.
**Rejected:** Backend rendering UI, or frontend holding the selection logic — both blur the agent/UI boundary.

### ADR-010 — Typed component-block SSE contract is the load-bearing seam (D-10)
**Decision:** Backend streams `{ type, pattern, props, meta }` blocks + `agent_step` events over SSE; frontend maps `pattern` → component and hydrates with `props`. Backend schema (`app/models/schemas.py`) and frontend mirror (`lib/blocks.ts`) must stay in sync.
**Why:** A single small contract is the only coupling between the two runtimes — easy to keep honest, easy to test.
**Rejected:** A fat REST API returning rendered HTML, or GraphQL — over-engineered for a stream of typed blocks. **Watch:** schema drift between the two files is the top maintenance risk; treat them as one change.

### ADR-011 — Config-driven multi-provider router (D-05)
**Decision:** Each agent declares a primary + ordered fallback chain in `providers/config.py`; `providers/router.py` executes it, falls through on error/refusal, logs provider + tokens/cost. Provider choice is a config edit, never code in an agent.
**Why:** Resilience against rate-limits/refusals; lets fast models serve the Diagnostician and stronger ones serve the Strategist. Chosen by the user over a single hard-coded provider.
**Rejected:** One hard-coded provider (brittle, not swappable). **Trade-off:** more integration surface; mitigated by a uniform adapter interface. The Anthropic adapter is implemented (lazy import); OpenAI fallback adapter lands with P1.

### ADR-014 — Anthropic Claude is the live primary provider (D-14)
**Decision:** Within the ADR-011 router, **Anthropic Claude** is the primary for every LLM agent — `claude-haiku-4-5` for the Diagnostician + Composer (latency-sensitive, structured), `claude-sonnet-5` for the Pedagogy Strategist (reasoning-heaviest). OpenAI is the configured fallback.
**Why:** Chosen by the user. Claude's reasoning + structured-output quality fits the diagnose→strategise→compose chain; hackAstone is provider-agnostic so nothing forces OpenAI there. The router keeps it swappable per D-05.
**Rejected:** OpenAI-primary (Codex-KL credits argue for it, but the user chose Claude; the fallback slot keeps OpenAI available). **Note:** confirm exact model ids via the Claude API skill when wiring P1; the router lazy-imports `anthropic` so the app still runs if the SDK/key is absent (degrades to scripted).

### ADR-012 — Learner store behind an interface: SQLite (dev) → Firebase (hosted) (D-11)
**Decision:** `LearnerStore` protocol; in-memory impl in P0, SQLite for local dev, Firebase for the hosted multi-device demo. The backend depends only on the interface.
**Why:** Don't pay Firebase setup/latency cost during early dev; keep the option open for a hosted demo without touching agent code.
**Rejected:** Firebase from day one — premature. In-memory forever — loses persistence, the whole point of the tutor loop.

### ADR-016 — Structured agent output via prompt-and-parse, not the SDK's native `output_config` (P1)
**Decision:** `ProviderRouter.run_structured()` instructs the model to reply with a single JSON object, extracts it with a fence/prose-tolerant parser, and repairs once on malformed output. The calling agent validates the dict into its Pydantic model and falls back to scripted P0 behaviour on any failure.
**Why:** One code path serves both the Anthropic primary and the OpenAI fallback, and it doesn't depend on a specific `anthropic` SDK version exposing `output_config` — the app must run on whatever SDK `uv` resolves. The repair pass + validation + scripted fallback is a stronger reliability story (never pass raw model text through as props, D-01) than trusting a single native call.
**Rejected:** SDK-native structured outputs (`output_config.format`) — cleaner when available, but couples us to a newer SDK and to Anthropic-only semantics. Revisit if we pin the SDK version. **Trade-off:** prompt-and-parse can occasionally need the repair pass; that's logged in `providers/metrics`.

### ADR-017 — Faithfulness pinned in code, not left to the model (P1, constraint #6)
**Decision:** The Composer merges a per-pattern `_FAITHFUL_PINS` table over the model-generated props, so science-critical fields (e.g. osmosis `correct_direction: toward-higher-solute`) are always correct regardless of what the model returns.
**Why:** Constraint #6 is non-negotiable and a science-literate judge will probe the sim. The model configures presentation; the physics is authored by us.
**Rejected:** Trusting the model to set the correct answer — one hallucinated field ships a wrong sim.

---

## Assumptions (surface at the next checkpoint)

- **CONFIRMED (OQ-1):** flagship = **osmosis** (Biology); the two other flagships are bonding-electrons (Chem) and forces-motion (Phys) — build these three first (D-13).
- **RESOLVED (OQ-2):** provider = **Anthropic Claude** primary, OpenAI fallback (D-14/ADR-014).
- **ASSUMED (OQ-3):** SQLite (or in-memory) through P3; Firebase only if a hosted multi-device demo is needed.
- **ASSUMED (OQ-4):** P0 agent nodes are scripted stubs; genuine LLM reasoning arrives P1 for the osmosis slice, then extends across the 12 concepts in P2.
- **ASSUMED (model ids):** `claude-haiku-4-5-20251001` / `claude-sonnet-5` — verify against the Claude API skill when wiring P1.
