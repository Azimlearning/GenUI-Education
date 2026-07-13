# GenUI test v2 — Level 2 Generative UI proof of concept

A minimal, working **Level 2 generative UI** app (see
[`../research/generative-ui-research-2026-07-06.md`](../research/generative-ui-research-2026-07-06.md) §2):
the model never returns prose — for every prompt it designs a purpose-built interface and returns
it as a **declarative JSON UI spec**, which a small React runtime renders from a fixed component
vocabulary.

**Nothing in the output is hardcoded.** Every screen is whatever JSON the model returned for your
prompt. Use the **"View raw spec"** toggle to see the exact spec behind the rendered UI.

## How it works

```
prompt ─► POST /api/generate ─► Claude (tool-forced render_ui call)
                                   │  returns { title, root: UINode tree }
                                   ▼
              components/Renderer.tsx renders the tree
              (column · row · card · heading · text · callout · badge · stat ·
               list · table · progress · barChart · slider · input · select · button)
                                   │
        user presses a button ─► action + ALL current input values sent back
        as the next conversation turn ─► model generates the NEXT UI state
```

- **The contract** lives in [`lib/uispec.ts`](lib/uispec.ts): the system prompt documents the
  vocabulary; the tool call guarantees parseable JSON (`tool_choice` forced).
- **The runtime** is [`components/Renderer.tsx`](components/Renderer.tsx): recursive, one React
  component per node type, unknown types degrade to a visible placeholder instead of crashing.
- **The round-trip**: sliders/inputs/selects hold local state; any button press sends the action
  string plus all input values back to the model, which returns the next interface state
  (calculators compute, quizzes reveal answers, plans go deeper).
- The API key stays server-side (`app/api/generate/route.ts`); the client never sees it.

## Run

```bash
bun install
cp .env.local.example .env.local   # add ANTHROPIC_API_KEY (already wired if copied from Synapse)
bun run dev                        # http://localhost:3210
```

## What "Level 2" means (and why this design)

- **Level 1** (Synapse today): model picks from pre-built components — fast, faithful, bounded.
- **Level 2** (this app): model composes *novel screens* as UI-as-data from a bounded vocabulary —
  expressive but safe: no generated code ever executes, so no sandbox is needed. Same idea as
  Thesys C1 and Google's A2UI protocol.
- **Level 3**: model writes real HTML/JS into a sandboxed iframe — maximally expressive, needs
  isolation. The natural next experiment (`GenUItestv3`?).

## Verified working (2026-07-06)

- `bun run build` clean (Next 16, React 19, TypeScript strict).
- Live test: "Compare renting vs buying a car in Malaysia" → 25-node spec (stats, barChart,
  table, callouts, selects, button) from `claude-sonnet-5` in ~16s.
- Round-trip test: button press with select values → new 26-node personalized calculator state
  (sliders, progress, stats).
