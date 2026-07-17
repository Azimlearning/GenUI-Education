# Axiom UI Upgrade, Handoff

This branch (`ui-upgrade`) redesigns the Axiom frontend end to end: a friendly
light-and-dark learning-app look, a mascot, and a locked design system. Behaviour
and the pipeline are untouched. This note is everything you need to pick it up.

## Source of truth (read these first)

- `design/BRAND.md`: the identity. Palette (teal = working, green = verified,
  gold = reward), typography, the chunky button form language, motion, voice,
  and the three hard bans (no glow, no background grid, no gradient wallpaper).
- `design/FLOW.md`: every screen and state dressed in the brand, from the front
  door to the pipeline to the verified reward.

The code implements those docs and reads semantic tokens (`bg-card`, `text-ink`,
`text-primary-ink`), never raw hex. If a component needs a colour, add or reuse a
token in `frontend/app/globals.css` + `frontend/tailwind.config.ts`, do not inline
a hex value.

## How to run

```
cd frontend
npm install
npm run dev            # localhost:3000, the front door works without the backend
```

Full app (frontend + backend + postgres):

```
make dev               # from sidequest/
```

Checks (all currently green):

```
cd frontend
npx tsc --noEmit
npx next lint
npx vitest run         # 14 tests
npx next build
```

## What changed

- Design tokens: light and dark palettes as CSS variables + a Tailwind theme.
- Fonts: Fredoka (display), Nunito (body), JetBrains Mono (the instrument
  texture), self-hosted via `next/font`, no CDN.
- Layout: a learning-app top bar (streak, gems, theme toggle, avatar), a real
  front door (hero question, example chips), and a two-column read-while-it-
  builds stage once a question is live.
- Components restyled: Composer, MessageList, StreamRenderer, ProgressStages,
  SandboxFrame, DegradedCard. New: TopBar, Mascot.
- Pipeline: a filling progress bar, stages that check off teal into green, the
  code appearing in a dark well. Verified lab celebrates the checkpoint with a
  "Science checked" badge and a little XP.
- Dark mode: retuned (not inverted), applied from the system preference, with a
  top-bar toggle that saves the choice and applies before first paint (no flash).
- New app icon (the orbiting-node logomark).

## Axi, the mascot

`frontend/components/Mascot.tsx`. Axi is the logomark node given a face, so the
logo, the mascot, and the tutor buddy are one identity. It takes a `mood`:

- `happy`: the front door greeting
- `thinking`: the "Axi is thinking" waiting state
- `celebrate`: the verified lab header (arms up, sparkles)
- `oops`: the degraded card

The idle float respects `prefers-reduced-motion`.

## Hard rules that were kept (do not break)

- The artifact iframe stays `sandbox="allow-scripts"` only. Never add
  `allow-same-origin`. See `SandboxFrame.tsx`.
- No runtime CDN. Fonts are self-hosted through `next/font`.
- No em dashes or en dashes in UI copy or docs.

## Not done yet (intentional, flagged so it is not a surprise)

- The in-conversation states (streaming, building, verified, degraded) are built
  and compile clean, but were only confirmed via build, not with live backend
  data (running the pipeline spends API credit). Worth a visual pass with
  `make dev` before demo day.
- Tutor buddy (Phase 5): the space is reserved and Axi is ready to drop in, but
  the tutor loop is not wired.
- Streak, gems, and XP are demo values in the chrome, not wired to real progress.

## Commits on this branch

- Lock the Axiom brand and flow (the two design docs)
- Apply the Axiom brand to the frontend, and add Axi the mascot
- Add dark mode and a theme toggle
