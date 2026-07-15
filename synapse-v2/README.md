# Synapse v2 — the Codex build

Turns a Malaysian Form 4–5 KSSM SPM science question into an **interactive lab experiment**, not a
wall of text. Built for [Codex Community Hackathon KL 2026](https://codexhackathon.my), Education
Access track, Team Dang Wangi.

Implements [`../Codex hackathon/codex-technical-spec.md`](../Codex%20hackathon/codex-technical-spec.md).

## Run

```bash
bun install
cp .env.local.example .env.local   # add ANTHROPIC_API_KEY
bun run dev                        # http://localhost:3200
bun test                           # 72 tests
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

The Planner picks the **lowest tier that can faithfully express the experiment**. Lower is faster
and more trustworthy; higher is unbounded.

| Tier | What the model does | When |
|---|---|---|
| **A** | Fills the typed slots of a pre-built science sim | A catalog component genuinely covers it |
| **B** | Composes a novel screen as UI-as-data, and may write the **formulas** that drive it | Nothing in the catalog fits |
| **C** | Writes a complete self-contained HTML/JS interactive | Neither tier can express it |

**Fallback chain: C → B → A → plain explanation.** Every failure lands on something that works, so
the demo never shows a dead end. When it degrades, the UI says so out loud.

### Tier A — pre-built, but adjustable

Five sims ([`lib/science/catalog.ts`](lib/science/catalog.ts)): concentration gradient, forces and
motion, bonding, circuits, refraction. Each declares a Zod slot schema. "Show me diffusion" and
"0.5 M NaCl vs 0.1 M across a partially permeable membrane at 37°C" hit the **same component** with
different slot values — the specificity comes from the student, the machinery is pre-built and
correct.

**Faithful pins are the reason to trust this.** Science-critical values are merged *over* whatever
the model proposed:

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

### Tier B — generated behaviour, without generated code

The model returns a JSON tree from a bounded vocabulary, via a forced tool call. Two things push it
past plain UI-as-data:

- **`science` nodes** embed a real Tier A sim inside a generated screen.
- **`computed` / `formulaChart` nodes** carry model-written formulas, evaluated by
  [`lib/expr.ts`](lib/expr.ts) — a recursive-descent parser over whitelisted maths. No `eval`, no
  `new Function`, no property access, no globals, no loops in the grammar. `window`, `alert(1)` and
  `x.y` are all parse errors.

### Tier C — the escape hatch

The model writes a whole interactive, rendered in `<iframe sandbox="allow-scripts">` **without**
`allow-same-origin` (granting both would let the frame strip its own sandbox), plus a CSP of
`default-src 'none'` and no `connect-src`. Our design tokens are injected so generated labs look
like the app; an injected `reportEvent()` bridge sends interactions back to the Guide.

While it streams, a provisional preview shows the lab's shape appearing, so a 40 second build reads
as the AI working rather than a hang.

## Layout

```
lib/contract.ts        the SSE event contract — the load-bearing seam
lib/router.ts          provider chain (Claude primary → OpenAI fallback), config-driven
lib/pipeline.ts        the five steps + the fallback ladder
lib/expr.ts            the restricted formula evaluator
lib/uispec.ts          Tier B vocabulary + validation
lib/sandbox.ts         Tier C prompt, safety checks, srcdoc assembly
lib/science/catalog.ts slot schemas + faithful pins
components/science/    the five sims
components/Renderer.tsx  Tier B runtime
components/Sandbox.tsx   Tier C host
app/api/pipeline/route.ts  the one endpoint
```

## Verified

Live against the API on 2026-07-15, plus `bun test` (72 tests), `tsc --noEmit`, and
`bun run build` — all clean.

| Flow | Measured | Result |
|---|---|---|
| Fast pass → gate | ~5s | Checker names the osmosis misconception before anything is built |
| Tier A | ~3s | Pins held against the model's own fill; picked 0 M vs 1.5 M for maximum contrast |
| Tier B | ~17s | 22-node composed screen |
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
