# Synapse v2 — the Codex build

Turns a Malaysian Form 4–5 KSSM SPM science question into an **interactive lab experiment** the AI
designs on the spot — not a wall of text, and not a component picked off a shelf. Built for [Codex Community Hackathon KL 2026](https://codexhackathon.my), Education
Access track, Team Dang Wangi.

Implements [`../Codex hackathon/codex-technical-spec.md`](../Codex%20hackathon/codex-technical-spec.md).

## Run

```bash
bun install
cp .env.local.example .env.local   # add ANTHROPIC_API_KEY
bun run dev                        # http://localhost:3200
bun test                           # 118 tests
```

Only `ANTHROPIC_API_KEY` is required. `OPENAI_API_KEY` is optional and enables the fallback leg of
the provider router.

## What it does

```
student prompt
     │
     ▼  one fast call — must feel instant
[1] PLANNER   what experiment fits; the lowest tier that can express it
[2] CHECKER   is the student's premise sound? if not, state the contradiction
[3] BRIEF     describe what will be built  →  "Generate Experiment"
     │
     ── student confirms ──  (skipped if they explicitly asked to generate)
     ▼
[4] GENERATOR build it, at the planned tier, degrading if that fails
[5] GUIDE     read what the student did; respond with insight
```

Every step streams to the pipeline panel as it happens. That panel is the oversight mechanism, not
decoration: the chosen tier, the filled science-critical values, and any flagged contradiction are
all on screen, so a wrong fill is catchable by a teacher rather than silent.

## The generation ladder

**The model designs the experiment. Tier B is the default**, and the pre-built sims are the
exception — three of them, kept only where being right matters more than being bespoke.

| Tier | What the model does | When |
|---|---|---|
| **B** | **Designs the lab**: state variables, physics formulas, a scene of shapes | The default. Almost everything. |
| **A** | Fills the typed slots of a pinned sim | Only the 3 documented misconceptions |
| **C** | Writes a complete self-contained HTML/JS interactive | Rare. Nothing else can express it. |

**Fallback chain: C → B → (A only if a pinned component was chosen) → plain explanation.** When it
degrades, the UI says so out loud. It will *not* degrade a generated pendulum into a trolley sim:
answering a question nobody asked is worse than an honest explanation.

### Tier B — the model designs the experiment

The headline. There is no "pendulum component" — there is a simulation primitive
([`lib/sim.ts`](lib/sim.ts)), and the model composes a pendulum out of it:

```jsonc
{"type": "sim", "spec": {
  "params": [{"id": "length", "label": "String length", "min": 0.2, "max": 2, "value": 1}],
  "state":  {"theta": "rad(amplitude)", "omega": "0"},
  "step":   {"omega": "omega - (g/length) * sin(theta) * dt",   // the real nonlinear pendulum
             "theta": "theta + omega * dt"},
  "derived":{"bobX": "pivotX + scale*length*sin(theta)"},
  "scene":  [{"shape": "circle", "cx": "bobX", "cy": "bobY", "r": "6 + mass*4", "fill": "phys"}],
  "predict": {"prompt": "Double the mass. What happens to the period?",
              "options": [{"label": "Stays the same", "when": "mass >= 0.05", "explain": "..."}]}
}}
```

That is a real generated output, not an illustration. Every numeric attribute is a formula run
through [`lib/expr.ts`](lib/expr.ts) — a recursive-descent parser over whitelisted maths. No `eval`,
no `new Function`, no property access, no globals, no loops in the grammar. `window`, `alert(1)` and
`x.y` are parse errors. So it is generated **behaviour** without generated **code**, and it renders
as a first-class part of the page rather than an iframe.

**`when` is the pin principle, generalised.** The model does not say which answer is correct — it
writes the *condition* under which each is true, and the runtime evaluates that against the
student's own sliders. Truth is computed at run time from their values, never baked in at
generation time. A `when` that references none of the experiment's variables is rejected as an
assertion: on the first live run the model wrote `when: "true"` for the right answer and
`when: "false"` for the rest, and the validator bounced it into a repair.

Every formula is probed at generation time against a scope of the declared names, so a typo costs
one repair round-trip instead of a lab that renders blank on stage. The screen's other nodes
(`computed`, `formulaChart`) can read the sim's sliders by id, so a chart beside the pendulum
tracks the student's hand.

### Tier A — the three we don't let it design

[`lib/science/catalog.ts`](lib/science/catalog.ts): osmosis, forces-and-motion, bonding. Each targets
a misconception documented in the SPM cohort, and each carries **pins** — science-critical values
merged *over* whatever the model proposed:

```ts
pins: {
  particle: "water",
  membrane: "selectively-permeable",
  correct_direction: "toward-higher-solute",
}
```

The model chooses the scenario. It does not get a vote on which way water moves. A model that fills
`correct_direction: "toward-lower-solute"` — the exact misconception the component exists to break —
still ships the correct sim. There's a test for precisely that.

If a component here doesn't have a pin, it shouldn't be here. Circuits and refraction used to be in
this list; the model builds better versions of both on demand.

### Tier C — the escape hatch

The model writes a whole interactive, rendered in `<iframe sandbox="allow-scripts">` **without**
`allow-same-origin` (granting both would let the frame strip its own sandbox), plus a CSP of
`default-src 'none'` and no `connect-src`. Our design tokens are injected so generated labs look
like the app; an injected `reportEvent()` bridge sends interactions back to the Guide.

While it streams, a provisional preview shows the lab's shape appearing, so the 75-95 second build
reads as the AI working rather than a hang.

## Layout

```
lib/contract.ts        the SSE event contract — the load-bearing seam
lib/router.ts          provider chain (Claude primary → OpenAI fallback), config-driven
lib/pipeline.ts        the five steps + the fallback ladder
lib/expr.ts            the restricted formula evaluator (no eval, ever)
lib/sim.ts             THE GENERATIVE SANDBOX — how the model designs an experiment
lib/uispec.ts          Tier B vocabulary + validation
lib/describe.ts        tells the Guide what's on screen (it can't see the lab)
lib/sandbox.ts         Tier C prompt, safety checks, srcdoc assembly
lib/science/catalog.ts the 3 pinned sims
components/science/GenerativeSim.tsx  runs whatever the model designed
components/science/*Sandbox.tsx       the 3 pinned sims
components/Renderer.tsx  Tier B runtime
components/Sandbox.tsx   Tier C host
app/api/pipeline/route.ts  the one endpoint
```

## Verified

Live against the API on 2026-07-15, plus `bun test` (118 tests), `tsc --noEmit`, and
`bun run build` — all clean.

| Flow | Measured | Result |
|---|---|---|
| Fast pass → gate | ~5s | Checker names the osmosis misconception before anything is built |
| Tier A (pinned) | ~3s | Pins held against the model's own fill; picked 0 M vs 1.5 M for maximum contrast |
| Tier B, screen only | ~17s | 22-node composed screen |
| **Tier B, designing a sim** | **~40s** | A pendulum, twice: full nonlinear equation of motion, correct 2.01s period, a "g (planet)" slider |
| Tier C | 75–95s | 22–28k char lab, real `Math.asin(n2/n1)`, no network refs |
| Guide | ~2–3s | Responds to the actual values the student used |

Two bugs the live run caught, both now fixed:

- **Tier C emitted nothing.** Sonnet 5 runs adaptive thinking when `thinking` is omitted (a silent
  change from Sonnet 4.6), and `max_tokens` caps thinking *plus* output — so it reasoned for three
  minutes and produced zero HTML. The router now sets `thinking` explicitly per role.
- **Tier B broke at 32k `max_tokens`.** The SDK refuses a non-streaming request that large before
  it hits the network. `runStructured` now streams and collects via `finalMessage()`.

The fallback chain caught the first one on its own — Tier C failed, degraded to Tier B, and the
student still got a lab. That is the design working, but it was masking a real bug, which is why
the pipeline panel now reports an empty generation as its own failure rather than "document too
short".

## Notes on the build

- **Single Next.js app, not FastAPI + Next.** The spec called for a Python backend; with four days
  and no backend written, one service in one language removes a deploy, a CORS surface, and a class
  of demo-day failures. The spec's *architecture* is intact — the SSE event contract, the tier
  ladder, the provider router, the validation seam are all as specified. Zod does what Pydantic was
  going to do. If the Python backend gets built, the frontend swaps an endpoint URL.
- **No persistence.** Stateless by design, as the spec says.
- **Runs on Claude by default.** The router's chains are config; reordering or dropping a provider
  is an edit to one object in `lib/router.ts`.
