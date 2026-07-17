# Axiom — Brand Identity

The source of truth for how Axiom looks, feels, moves, and speaks. Code implements
this; when the two disagree, fix the code or change this doc, not neither.

Audience: Malaysian Form 4-5 (SPM) science students on a phone, and hackathon judges
watching on a projector for five minutes. Both have to believe this is a real product.

---

## 1. The idea in one line

**Ask a question. Watch it get built, and checked, in front of you.**

Axiom is not a chatbot that types paragraphs. It designs a working experiment for your
question, verifies the science is right, and hands it to you to play with. The brand has
to carry two feelings at once:

- **Trust.** The science is checked. This is the thing a chatbot cannot promise, and it
  is the whole reason to believe Axiom over ChatGPT. Every "checked" moment has to feel
  earned and real.
- **Wonder.** It is about discovery, not homework. A student should feel a small pull of
  curiosity, and a small hit of reward when something clicks.

The surface that carries those two feelings: **a friendly learning app, with the science
kept real.** Think the warmth and momentum of Duolingo (light, rounded, chunky,
rewarding), pointed at true science instead of vocabulary drills. Clean, never cluttered,
never toylike.

## 2. The philosophy: scaffolded discovery

Every education UI is really managing one thing: a learner's confidence. Four principles
drive every screen, and each one has to be visible on the screen, not just written here.

1. **Chunky and friendly.** Big pressable buttons, rounded cards, generous space. Nothing
   intimidating. It should feel good to poke at. Friendly comes from softness and space,
   never from cartoon color.
2. **Celebrate the checkpoint.** When the science checks out, you feel it: a green badge,
   a little XP, a real reward. The verified moment is the peak of the screen, treated like
   a completion, not a footnote.
3. **One clear next step.** Never a wall of options. Always one obvious thing to do next,
   so nobody gets stuck. One primary action per screen, everything else subordinate.
4. **Color narrates.** Teal is the machine working. Green is the science confirmed. A
   judge who never reads a word still sees teal turn to green.

## 3. Name and voice

**Axiom** is a truth taken as self-evident, the starting point everything else is proven
from. It fits a product whose promise is verified truth. Say it plainly; never dress it up
with taglines like "revolutionary" or "AI-powered."

**Voice:** confident, curious, plainspoken, a little warm. We talk *to* a smart
sixteen-year-old, never down to them, and never over their head.

- Say "Watch it get built and checked," not "Leveraging generative AI to synthesize
  pedagogical artifacts."
- Say "That is the misconception," not "Your input contains a factual inaccuracy."
- Say "Nice. Science checked, plus 10," not "Loading, please wait..."
- Short sentences. Real words. One idea at a time.
- Reward language is allowed and encouraged ("Nice," "plus 10 XP," "3 day streak"), but it
  stays quiet and never overpromises. We celebrate a real result, not a click.
- No em dashes or en dashes anywhere (commas, periods, or parentheses instead).
- No emoji in the product chrome. Ever. SVG icons only.

Microcopy examples:
- Empty state: "Ask a science question. Why does ice float? How does a kidney clean blood?"
- While building: "Designing the experiment... checking the science..."
- Verified badge: "Science checked"
- Reward on verify: "+10 XP"
- Degrade: "I could not build a safe interactive for this one, so here is the explanation."

## 4. Colour

A bright, warm-neutral canvas, not flat white and not cream. Light-committed by design:
it suits a friendly learning app, reads crisp on a projector, and is calm to read on a
phone. One teal, one green, one gold, each with a job. Bright, but disciplined: three
accents means three meanings, never wallpaper.

### Canvas (light, the one committed theme)

| Token | Hex | Role |
|---|---|---|
| `--canvas` | `#F7F8F4` | Page. Bright airy warm-neutral, faint teal bias so it reads chosen. |
| `--band` | `#EFF2EB` | Alternating section band, quiet grouping. |
| `--card` | `#FFFFFF` | Raised: cards, the composer, the artifact frame, the lab. |
| `--ink` | `#2F3A34` | Primary text. Soft near-black with a teal cast (never pure black). ~11:1 on `--canvas`. |
| `--ink-dim` | `#61706A` | Secondary text, captions. AA on `--canvas`. |
| `--ink-faint` | `#9AA49E` | Labels, placeholders, disabled. |
| `--line` | `#E4E8DF` | Hairline borders (used at 2px for the chunky look). |
| `--line-2` | `#D3DACE` | Stronger dividers, input borders, button under-edges. |

### The accents (this is the brand)

The colour system tells the product's story on its own. **Teal is the machine working.
Green is the science confirmed. Gold is the reward.**

| Token | Hex | Meaning |
|---|---|---|
| `--primary` | `#12A594` | Working teal, bright. Graphics, accents, the caret, the live node, the logomark. |
| `--primary-btn` | `#0A776B` | Button fill. Deep enough for white text at AA. |
| `--primary-edge` | `#075247` | The 3D pressed bottom edge under a teal button. |
| `--primary-soft` | `#E1F3EF` | Tinted fill behind live things (the tutor bubble, the eyebrow pill). |
| `--verify` | `#1FA35B` | Verified green, celebratory. The "science checked" badge fill, the passed stage node. |
| `--verify-edge` | `#157A42` | The 3D bottom edge under a green element. |
| `--verify-soft` | `#E4F6EA` | Verified badge / card tint. |
| `--verify-ink` | `#147E43` | Green used as text on white (AA). |
| `--gold` | `#E6A200` | Reward. Streak flame, gems, "+10 XP". Never a structural action colour. |
| `--gold-soft` | `#FCF1D3` | XP pill / reward tint. |
| `--warn` | `#B5720C` | Revising, caution. Honest, not alarming. |
| `--danger` | `#C24A42` | Failed, destructive, error. |

`--on-primary`: `#FFFFFF` sits on `--primary-btn` and `--verify` fills.

The gold is a supporting reward colour, not a fourth brand voice. It shows up small (a
streak count, an XP pill, a sparkle) and never as a page-level surface or a primary button.

### No glow, no grid, no gradient wallpaper

Three hard bans, learned the hard way. They are the tells that make a design read as
AI-generated:

- **No neon glow.** Accents are printed flat as fills and edges, never a `box-shadow`
  halo of colour. The only "light" is the soft neutral elevation shadow under a card.
- **No technical background grid, no starfield, no film grain.** The ground is clean
  paper. Whitespace and 2px hairlines do the spacing.
- **No decorative gradient.** The only gradients allowed are functional and subtle: the
  teal-to-green fill inside the progress bar, and the avatar disc. Never a hero gradient.

### Light mode is the product; dark mode is deferred

Ship light. It is the committed theme and everything above assumes it. If dark mode is
ever added (post-hackathon), retune rather than invert: darken the canvas to a warm near
black, lift the accents one step for contrast, keep the same three jobs. Do not build it
for the demo.

## 5. Typography

Three faces, each with a job. All self-hosted via `next/font` (no runtime CDN, which also
honours the repo's no-CDN rule and kills layout shift).

| Face | Use | Why |
|---|---|---|
| **Fredoka** | Display and brand: the wordmark, hero question, section headings, button labels, stat counters. 500/600. | Rounded, warm, friendly with structure. Reads like a learning app without tipping into kid-stuff. |
| **Nunito** | All UI and body text. 500/600/700. | Rounded humanist workhorse. Warm, trustworthy, superb at small sizes on a phone, very legible. |
| **Berkeley Mono** | The code preview, formulas, tabular numbers, stage tags, kickers. 400/500. | The texture of "real science being written." Ties the verify story to something you can watch. (Fallback: JetBrains Mono.) |

Nunito runs a little heavier than a neutral sans (base weight 500), which is what gives the
UI its friendly density without shouting.

### Scale (8pt rhythm)

| Role | Font | Size / line | Weight |
|---|---|---|---|
| Display | Fredoka | 36-60 / 1.04 | 600 |
| H1 | Fredoka | 29-30 / 1.1 | 600 |
| H2 | Fredoka | 24-25 / 1.2 | 600 |
| Body | Nunito | 16 / 1.55 | 500 |
| Body-emphatic | Nunito | 16 / 1.55 | 700 |
| Body-sm | Nunito | 14 / 1.5 | 600 |
| Button | Fredoka | 16 / 1 | 600, +0.02em |
| Label / kicker | Berkeley Mono | 11-12 / 1.4 | 400, +0.09em, uppercase |
| Code | Berkeley Mono | 11.5 / 1.55 | 400 |

Body is 16px minimum on mobile (no iOS auto-zoom). Numbers in readouts, timers, streaks,
and XP use `font-variant-numeric: tabular-nums` so values do not jitter as they change.

## 6. Form: shape, depth, motion

**Radius:** 12 (controls, small chips), 18 (cards, inputs, buttons), 24 (the browser
frame, the artifact frame, modals). Rounded and friendly, one step per level.

**Depth comes from two devices, used together:**

- **The chunky bottom edge (the signature).** Pressable things (primary and ghost buttons,
  the avatar, done-state nodes, chips) sit on a solid 3-4px darker edge of their own colour
  (`--primary-edge`, `--verify-edge`, `--line-2`). On press they translate down 3px and the
  edge shrinks, so tapping feels physical. This is the single most recognisable Axiom
  interaction, borrowed from the best learning app there is.
- **Soft neutral elevation.** Cards lift on one soft shadow (`0 8px 26px -10px` at low
  alpha, neutral not coloured). The browser/artifact frame gets a larger version. Borders
  are 2px hairlines, not heavy.

**Motion** (all respect `prefers-reduced-motion`):

- Micro-interactions 60-220ms. Enter ease-out, exit faster.
- Press: the chunky translate-down (3px) with the edge collapsing. Springy, immediate.
- The pipeline stages reveal staggered ~40ms apart; the active node pulses softly (opacity,
  not a glow); the progress bar fills left to right, teal into green.
- The verified moment is the one celebration: the badge pops in with a small scale, a
  couple of sparkles, the XP pill. Brief and earned, never confetti spam.
- Never block input during animation. Never animate width/height (transform/opacity only).

The motion philosophy: **motion is momentum.** A 60-second generation has to feel alive and
moving forward (staged progress, filling bar), and a success has to feel like a win (the
checkpoint pop). Elsewhere, motion is quiet.

## 7. Iconography and gamification

- **Icons:** Lucide (stroke icons), ~1.7px stroke to match the chunky weight, 20px default
  in UI, 16px inline. One family, one weight. No emoji as structural icons. The verified
  badge is a check; the live/thinking state is a soft pulsing node, not a spinner.
- **Gamification, kept light.** A streak flame with a day count and a gem count live in the
  top bar, so Axiom reads as a place you come back to. Verifying an experiment earns a small
  XP pill. These are real, quiet motivators, never nag banners, never blocking modals, never
  the point of the screen. The science is the point; the reward just marks it.

## 8. What this is not

- Not a neon HUD or a dark dashboard. Thin cyan-on-black sci-fi fails contrast and reads as
  "generic AI." We ship light and flat.
- Not a background grid, starfield, or film-grain texture. Those are AI tells. The ground is
  clean paper.
- Not claymorphism, not a cartoon mascot, not baby-bright kid-stuff. Friendly and rounded,
  yes; toylike, no. Sixteen-year-olds and judges both distrust toylike.
- Not a chatbot dashboard. No dense sidebars, no settings-gear chrome, no "assistant is
  typing." The screen is about the experiment, not the conversation.
- Not decorative. Every accent, edge, badge, and animation earns its place by carrying the
  trust-or-reward story. When in doubt, remove it.

## 9. Token reference (for the code)

The values above land in `frontend/app/globals.css` as CSS variables and in
`frontend/tailwind.config.ts` as the theme. Components read semantic tokens
(`bg-card`, `text-ink-dim`, `text-primary`, the chunky `.btn` classes), never raw hex.
See `design/FLOW.md` for how these dress each screen and state.
