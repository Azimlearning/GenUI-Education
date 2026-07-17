# Synapse v2 — Technical Specification (Codex Hackathon Build)

> Companion to [`codex-project-scope.md`](codex-project-scope.md) (problem/objective/scope — read
> that first). This doc is the technical layout of the **whole-new app** being built for Codex
> Demo Day (18 July 2026). Last updated: 2026-07-13.
>
> **What this build is:** a full upgrade of Synapse, rebuilt fresh (not an evolution of the
> existing `../Synapse/` monorepo). Same name, new engine: instead of only *selecting* pre-built
> components, the model *generates* the interactive lab experience — through a tiered generation
> system that sits between Level 2 and Level 3 generative UI, with a full Level 3 escape hatch.

---

## 1. System overview

```
student prompt
     │
     ▼
┌──────────────────────── Python backend (FastAPI, SSE) ────────────────────────┐
│                                                                               │
│  Visible pipeline (each step streamed live to the UI as it happens):          │
│                                                                               │
│   [1] PLANNER      what experiment fits this question; which tier can        │
│                    express it (slots / spec / generated code)                │
│   [2] CHECKER      is the student's premise scientifically sound? if not,    │
│                    state the contradiction plainly                           │
│   [3] BRIEF        short description of the experiment to be built           │
│                    → UI shows it + a "Generate Experiment" button            │
│                    (skipped if the prompt explicitly asked to generate)      │
│        ── student confirms ──                                                 │
│   [4] GENERATOR    produce the interactive: fill component slots, compose    │
│                    the UI spec, or write sandboxed code (see §3 tiers)       │
│   [5] GUIDE        during interaction: receive events, provide insight,      │
│                    generate the next UI state                                │
│                                                                               │
│  + Provider Router: every LLM call goes through a config-driven chain        │
│    (primary + fallback, no hard-coded vendor)                                │
└───────────────────────────────────────────────────────────────────────────────┘
     │  SSE: pipeline_step · brief · ui_spec · generated_code · guidance
     ▼
┌──────────────────────── Next.js frontend (TypeScript, Tailwind) ──────────────┐
│  Pipeline panel (visible reasoning) · Spec renderer (§4) · Science component │
│  library with slots (§5) · Sandboxed iframe host for Level 3 (§6) ·          │
│  Event bridge back to the backend (§7)                                       │
└───────────────────────────────────────────────────────────────────────────────┘
```

- **Stateless demo:** no accounts, no cross-session persistence. Conversation history lives in
  the current session only.
- **The pipeline is rebuilt fresh** — it is *not* the Synapse v1 LangGraph agents, learner store,
  misconception KB, or teacher dashboard. The contradiction check runs on the model's own
  knowledge, not a pre-authored library.

## 2. Stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | Next.js (App Router) · TypeScript · Tailwind · bun | Renderer + component library + sandbox host |
| Backend | Python 3.13 · FastAPI · Pydantic v2 · `sse-starlette` | Pipeline orchestration, provider router, spec validation |
| Contract | SSE stream of typed events (`pipeline_step`, `brief`, `ui_spec`, `generated_code`, `guidance`, `done`) | Pydantic models mirrored by TypeScript types — the load-bearing seam |
| LLM runtime | Provider Router: Anthropic Claude (Sonnet 5) primary · OpenAI GPT fallback | Config-driven order; swappable without code changes. Claude is the verified path (GenUITestV2 live tests, 2026-07-06) |
| Build tooling | Codex (AI coding tool) for scaffolding and acceleration | This is the "Technical Execution with Codex" judging story — build tool, not runtime |
| Persistence | None (stateless) | Deliberate scope cut for demo safety |

## 3. The generation ladder (the core of the build)

Three tiers, escalated per question. The Planner picks the *lowest tier that can faithfully
express the experiment* — lower tiers are faster and safer; the top tier is unbounded.

### Tier A — Science components with slots (fast path)

Pre-built, high-fidelity interactive science components (simulation sandboxes) whose **slots**
the model fills with the user's specific ask. The components are adjustable, not fixed demos:

| Component (example) | Slots the model fills |
|---|---|
| Reaction sandbox | specific reactants/products, the balanced equation, molar quantities, conditions |
| Concentration-gradient sandbox | the specific substances/membrane scenario (osmosis, dialysis, gas exchange), initial concentrations |
| Cell explorer | the specific organism and cell type, which organelles to highlight |
| Physics motion sim | the student's specific numbers — masses, forces, angles, velocities |
| Circuit builder | specific components and values (resistances, voltage) |
| Graph/relationship explorer | the specific formula and variable ranges |

A slot is a typed prop with a schema the model must satisfy (validated server-side with Pydantic
before the spec is streamed). So "show me diffusion" and "show 0.5 M NaCl vs 0.1 M NaCl across a
partially permeable membrane at 37°C" hit the *same component* with different slot values — the
specificity comes from the student, the interactive machinery is pre-built and correct.

### Tier B — Declarative UI spec + model-written logic in slots (middle path)

When no single science component fits, the model composes a **novel screen as UI-as-data**: a
JSON tree from a bounded node vocabulary (layout, text, callout, stat, table, chart, slider,
input, select, button — extending the contract proven in `../GenUITestV2/lib/uispec.ts`), with
the Tier A science components available *as nodes inside the tree*.

What pushes this beyond plain Level 2: designated slots may carry **model-written logic** — a
formula or small expression (e.g. the specific physics equation driving a sim, a reaction-rate
function) executed in a **restricted expression evaluator** (whitelisted math operations, no DOM,
no I/O, no loops beyond bounds). Generated *behaviour* without shipping generated *code* to the
host page.

### Tier C — Full Level 3 escape hatch (unbounded path)

When the question needs an interactive that neither tier can express, the model **writes a
complete self-contained HTML/JS interactive**, rendered in a **sandboxed iframe** (§6). This is
the "the AI designs your lab from scratch" moment — slower and riskier, so it is the escalation
target, not the default.

**Fallback chain (never dies):** Tier C failure → retry once with error context → degrade to
Tier B spec → degrade to Tier A closest component → plain guided explanation. Every failure mode
lands on something working.

## 4. The UI spec contract (Tier B)

- Single source of truth: one schema file per runtime (Pydantic model backend-side, TS types
  frontend-side), kept in sync — the system prompt documents the vocabulary to the model, the
  renderer implements it, the validator enforces it.
- The model returns the spec via a **forced tool call** (`render_ui`), guaranteeing parseable
  JSON — no prose-wrapped code blocks to scrape (mechanism verified in GenUITestV2: 25-node spec
  in ~16 s on Sonnet 5).
- Renderer rules: recursive; one React component per node type; **unknown node types degrade to
  a visible placeholder, never a crash**; root is a column; depth/size caps enforced.
- Science components (Tier A) appear as first-class node types in the vocabulary, so a Tier B
  screen can embed a faithful sim next to generated explanatory UI.

## 5. The slot system (how "pre-built but adjustable" works)

1. Each science component declares a **slot schema**: typed, bounded props (numbers with ranges,
   enums for scenario variants, strings for labels/formulas) plus which slots are
   student-fillable at runtime (rendered as inputs) vs. model-filled at generation time.
2. The Planner's component catalog carries these schemas, so the model knows exactly what each
   component can be specialised into.
3. The Generator fills slots from the student's specifics; the backend **validates every slot
   value against the schema** before streaming. Out-of-range or malformed → one repair round-trip
   with the validation errors, then fallback.
4. Science-critical slot values (equations, directions, constants) are echoed into the visible
   pipeline step so a wrong fill is *visible*, not silent.

## 6. Level 3 sandbox (Tier C mechanics)

Non-negotiable rule (consistent with every surveyed implementation in
[`../research/generative-ui-research-2026-07-06.md`](../research/generative-ui-research-2026-07-06.md) §6.2):
**generated code never touches the host DOM.**

- Rendered via `<iframe srcdoc>` with a restrictive `sandbox` attribute (`allow-scripts` only —
  no same-origin, no top navigation, no popups) + CSP blocking network access.
- **Design-system injection:** the app's CSS variables/tokens and base styles are injected into
  every sandbox so generated interactives look like Synapse, light/dark aware — novel structure,
  consistent skin.
- **Event bridge SDK:** a tiny injected `reportEvent(...)` forwards interactions
  (`postMessage`) to the host, which relays them to the Guide step — so even fully generated
  interactives feed the guidance loop.
- **Progressive rendering:** generated HTML streams token-by-token into a provisional preview
  (morphed DOM updates, skeleton shown from the first token) so the ~30–60 s worst-case
  generation reads as "the AI is building your lab" rather than a hang.

## 7. Interaction round-trip (the Guide loop)

Every interactive — all three tiers — reports interactions through one event shape:
`{ source: node_id | sandbox, action, values }`.

- Tier A/B: input nodes carry unique ids; button presses send the action + all current input
  values (GenUITestV2's proven round-trip).
- Tier C: same payload via the sandbox event bridge.
- The Guide receives the event with conversation context and responds with **insight and
  guidance** (the "with guidance, not just a toy" part of the objective): interprets what the
  student's manipulation showed, nudges the next prediction, answers follow-ups, and when
  warranted generates the next UI state.

## 8. The confirm-before-generate flow (technical form)

1. Prompt arrives → Planner + Checker + Brief run as one fast streamed pass (small/fast model via
   the router — this must feel instant).
2. UI renders the brief: what will be built, what the student will be able to manipulate, and —
   if the Checker found a contradiction in the student's premise — a plainly-stated correction
   callout *before* any generation.
3. **Explicit-intent bypass:** if the Checker classifies the prompt as an explicit generation
   request ("generate/build/make me the experiment…"), the confirm gate is skipped and generation
   starts immediately; the brief still streams alongside as context.
4. On "Generate Experiment": the Generator runs at the tier the Planner chose, streaming progress
   into the visible pipeline panel.

## 9. Provider router

- Config file defines an ordered provider chain per pipeline step (e.g. fast model for
  Planner/Checker/Brief, strongest model for Generator Tier C).
- Adapters normalise the two SDKs behind one `run_structured()` interface (forced tool call in,
  validated Pydantic model out).
- Primary: Anthropic Claude (Sonnet 5) — the verified generation path. Fallback: OpenAI GPT.
  Reordering is config-only. Keys live in `backend/.env`, never client-side, never
  `NEXT_PUBLIC_`.
- Router logs per-call latency/model — feeds both debugging and the demo's responsible-AI story.

## 10. Latency budget & mitigations

| Stage | Target | Mitigation |
|---|---|---|
| Brief (plan+check+describe) | < 3 s to first token | Fast model; single combined call; streamed |
| Tier A generation | < 5 s | Small structured output (slot values only) |
| Tier B generation | ~10–20 s | Forced tool call streamed; renderer paints progressively |
| Tier C generation | 30–60 s worst case | Progressive streaming preview (§6); confirm gate absorbs the wait as an *expected* build step; Tier A/B fast path for everything the catalog can express |

## 11. Reliability & responsible AI

- **Validation before render:** every spec/slot payload is schema-validated server-side; every
  Tier C artifact is sanity-checked (parses, no external network refs) before streaming.
- **Repair loop:** one automatic retry with the validation/console errors appended, then fall
  down the tier chain (§3). The demo never shows a dead end.
- **Accuracy posture:** science-critical machinery (sim physics, reaction correctness) lives in
  pre-built Tier A components wherever possible; model freedom is spent on *composition and
  specificity*, not on re-deriving physics. The Checker's contradiction statement is shown to the
  student rather than silently "fixed."
- **Transparency:** the visible pipeline panel is the oversight mechanism — every decision
  (chosen tier, filled slot values, flagged contradiction) is on screen.
- **Isolation:** generated code runs only inside the sandbox (§6); no student input ever becomes
  executable outside it.

## 12. Build plan (remaining days to 18 July)

| Day | Milestone |
|---|---|
| 13–14 Jul | Skeleton: FastAPI SSE pipeline (all 5 steps stubbed), Next.js shell, spec contract + renderer ported/extended from GenUITestV2, provider router with both adapters |
| 14–15 Jul | Tier A: 3–4 science components with slot schemas + validation + the confirm-gate flow end to end |
| 15–16 Jul | Tier B logic-slots evaluator · Tier C sandbox host + event bridge + design-system injection · fallback chain |
| 16–17 Jul | Guide loop round-trip · latency polish · demo script + rehearsal · deploy decision executed (public URL vs. laptop + recorded backup) |
| 18 Jul | Demo Day |

**Scope guardrail:** Tier A + confirm gate + visible pipeline is the *minimum demoable product*
and lands first. Tier C is the showpiece but is built strictly after the fallback chain exists.

## 13. Verification

- Backend: pytest on spec validation, slot-schema enforcement, router fallback, tier-degradation
  chain.
- Frontend: `tsc --noEmit` + production build clean; renderer snapshot on the vocabulary;
  unknown-node degradation test.
- Live: scripted end-to-end runs of the three demo flagship prompts at each tier, timed against
  the latency budget (§10) — rehearsed before Demo Day.
