# Axiom — App Flow and Screen Design

How the brand (`design/BRAND.md`) dresses the real flow. Grounded in the components that
exist today: `app/page.tsx`, `components/chat/*`, `components/artifact/*`. This doc is the
plan the redesign implements; it does not change what the pipeline does, only how it looks
and feels.

The spine of the experience: **one question, one unfolding answer.** Not a chat log to
scroll, an experiment being built for you, on a friendly learning surface that rewards you
when the science checks out.

---

## 0. Layout shift: from chat log to a learning screen

Today the app is a max-w-3xl chat column: user bubbles right, assistant replies stacked,
scroll history. That reads as "AI chatbot," which is the one thing we were told to avoid.

The redesign keeps the same components and data flow but reframes the arrangement into
something that reads as a learning app:

- **A slim top bar** carries the wordmark, the streak flame, the gem count, and the avatar.
  It makes Axiom feel like a place you return to, not a one-off text box. (Streak and gems
  are light motivators per BRAND section 7; they are decorative-of-progress, never blocking.)
- **First run is a centred stage,** not an empty chat: a friendly eyebrow pill, a large
  hero question, the composer as a big rounded input with a chunky "Build it" button, and
  three example questions as pill chips. It looks like the front of a product.
- **After you ask, the answer takes over the stage.** The question sits at the top as a
  small "Your question" context line; the streaming explanation and the building experiment
  are the focus. Prior turns collapse into "My questions" (reachable from the top bar),
  rather than an ever-growing scroll.
- **Desktop / projector:** a comfortable centred column (max ~1060px). While a question is
  live, the stage splits into two columns: the explanation to read on the left, the
  experiment building on the right.
- **Mobile:** the two columns stack (explanation first, then the build). Full width with
  16px gutters, 44px targets, composer pinned to the bottom above the safe area.

## 1. First run (the front door)

The judge's first three seconds. It must say "friendly, premium learning app" instantly.

- **Top bar:** logomark + "Axiom" in Fredoka 700, a 5 day streak flame in gold, gems, the
  avatar disc (with its own chunky bottom edge).
- **Eyebrow pill** in `--primary-soft`: "Learn by watching it get built."
- **The hero question** in Fredoka 600, large, with the last word ("checked") in
  `--verify-ink` green so the promise is legible at a glance.
- **One line of promise** in `--ink-dim`: "Axiom designs a working experiment for your
  question, checks the science is right, and hands it to you to play with."
- **The composer** is the hero action: a big rounded input (2px border, Nunito placeholder)
  next to one chunky primary button, "Build it." One clear next step, per the philosophy.
- **Three example chips** below, real SPM questions: "How does a kidney clean blood?",
  "What is total internal reflection?", "Why is the sky blue?". Tapping one fills and sends.
  Zero-typing path for a nervous demo, and a hint about scope.
- Quiet. No feature grid, no marketing. The product is the point.

## 2. Asking (commit)

- The composer commits: the question lifts to the top of the stage as a small "Your
  question" line (a back chevron + the question in Fredoka).
- Press feedback on "Build it": the chunky button presses down 3px, edge collapsing.
- Immediately, the two-column stage appears. No dead air. First visible activity lands under
  2s (the architecture already hits 1.7-1.9s to the planning stage).

## 3. The two things happening at once

Axiom fans out: the explanation streams while the experiment builds. On desktop they are
side by side so the parallelism reads as capability; on mobile they stack, explanation
first.

### 3a. The explanation (StreamRenderer)

- Body text (Nunito 500/16.5) streaming token by token with the `--primary` teal caret.
- Sits in a clean block, no chat bubble. This is Axiom talking, not a chat message.
- Readable measure (60-75 chars). Never full-width on a wide screen.
- **The tutor guide** lives here when it fires (Phase 5): a small node "buddy" with a
  rounded speech bubble in `--primary-soft`, one warm nudge. "Try this. Drag the temperature
  below 4 degrees and watch the density flip." Designed in now, not bolted on later.

### 3b. The pipeline (ProgressStages) - THE judge moment

This is the differentiator made visible. It has to feel like watching a mind work, not a
loading spinner, and it has to feel like *progress*, like a lesson advancing.

- A titled card ("Building your experiment") on `--canvas` inside a 2px rounded frame.
- **A header row** with the current stage name (Fredoka 600) and a progress pill,
  "3 of 5", in `--primary-btn` on `--primary-soft`.
- **A thick glossy progress bar** (12px, rounded, inset shadow, a highlight strip) filling
  left to right, `--primary` teal into a brighter teal. This is the momentum cue.
- The five stages as a checklist with chunky nodes:
  `designing the experiment -> building the interactive -> checking the science ->
  revising after review -> polishing`.
  - **pending:** node is a hollow 3px `--line-2` ring, label `--ink-faint`, tag "next".
  - **active:** node is a hollow `--primary` ring with a softly pulsing teal dot, label
    `--ink` 600, tag "working" in teal.
  - **done:** node fills `--verify` green with a white check and its own chunky bottom edge,
    label `--ink-dim`, tag "done" in green. The moment a stage passes, it turns green: a
    judge sees teal work turn green.
  - **revising:** only appears if it happens, node/tag in `--warn`. Showing this is a
    feature; label it "revising after review" so the honesty reads as rigour.
- **"Watch the code being written"** (the artifact_delta preview): a `<details>` under the
  stages. Open, it shows the generated HTML streaming in Berkeley Mono on a dark
  `#12211D` well (the one dark surface in the product, because code reads best dark, and it
  looks like a real editor). Catnip for judges: real code, appearing live.
- **No shimmer, no glow.** The momentum comes from the filling bar and the staged nodes,
  not an aurora sweep. That was the AI tell; it is gone.

## 4. The experiment is ready, and checked (SandboxFrame)

The payoff, and the checkpoint. This is where the philosophy's "celebrate the checkpoint"
lands.

- The lab card sits on `--card` inside a 2px `--verify-soft` rounded frame with a green
  chunky bottom edge, so the whole card reads "confirmed."
- **The header carries the reward:** a one-line title (Fredoka 600) on the left; on the
  right, a gold "+10 XP" pill and a chunky green "Science checked" badge (white check on
  `--verify`, its own bottom edge). This is the trust payload plus the dopamine hit. It is
  the sentence "unverified artifacts structurally cannot reach the client" turned into one
  glance a student actually enjoys.
- The sandboxed iframe below, on `--canvas`, its own scroll, sized to content, never
  overflowing the page.
- **Entrance is the one celebration:** the badge pops in with a small scale, the XP pill
  arrives, two small sparkles (one gold, one green) fire once near the experiment. Brief and
  earned. Behind `prefers-reduced-motion` the pop becomes a plain fade.
- Quiet chrome: a small chunky ghost "Try again" affordance, understated.

## 5. When it degrades (DegradedCard)

The fallback is a feature, and the design should carry it with dignity, not apology.

- Same rounded card, a 3px `--warn` left border (not `--danger` unless it truly failed).
- Honest copy in the brand voice: "I could not build a safe interactive for this one, so
  here is the explanation." The explanation text is still there and complete.
- A clear chunky "Try again" button (`--primary`, primary) when retryable.
- No XP, no celebration here. We only reward a real, verified result. But it is never a dead
  end, never a raw stack trace, never an apology.

## 6. Interacting and the tutor (Phase 5, design ahead)

Not built yet, but the design leaves room so it is not bolted on later (see 3a):

- When a student drags a control in the artifact, the **tutor buddy** speech bubble updates
  with a short, warm nudge, one line, in `--primary-soft`. "You set the angle to 60 degrees
  and the ball went further. What happens past 45?"
- It reads as a teacher leaning in, one line, never a wall. The node buddy + bubble style is
  reserved now.

## 7. The logomark and the buddy

A small mark that carries the whole idea: a single **node** (a filled `--ink` dot) with two
fine orbit ellipses, one stroked `--primary` teal, one `--line`. A point of certainty (the
axiom) with things in motion around it (the science you explore). Works at 26px in the top
bar and 512px as the app icon. Monoline, so it inverts cleanly and makes a clean favicon.
The same node, dropped into a `--primary-soft` disc, becomes the **tutor buddy** avatar, so
the brand mark doubles as a friendly character without needing a cartoon mascot.
(`app/icon.svg` gets replaced with this.)

## 8. The five-minute demo, mapped to the design

The design exists to make this sequence land:

1. **Front door (3s):** friendly premium first frame, streak and gems in the bar. "This is a
   real product people come back to."
2. **Ask "why does ice float" (2s):** question commits with a chunky press, the two-column
   stage appears instantly. No dead air.
3. **The pipeline works (30-60s):** the progress bar fills, stages check off teal into
   green on "checking the science," the code streams in the dark preview well. This is the
   wow. Narrate it: "it is designing the experiment, and now it is checking its own physics."
4. **Green check plus the reward (instant):** the "Science checked" badge pops, "+10 XP"
   arrives, the interactive appears, drag the control, the ice sits 92% submerged. The payoff
   people feel.
5. **Ask a hostile or nonsense question (optional):** it routes to text, no artifact, no XP,
   no spend. "It knows when not to build one, and it only rewards a real result." Rigour.

Every screen above is built so that sequence looks inevitable.

## 9. Accessibility and responsive (non-negotiable, per BRAND section 6 and the repo rules)

- Contrast: every pairing in BRAND section 4 meets AA. Teal and green are used as text only
  at their `-btn` / `-ink` weights; the bright `--primary` and `--verify` are for fills and
  graphics. Re-check any new combination.
- Motion: everything behind `prefers-reduced-motion`. The pulse becomes static, the checkpoint
  pop becomes a fade, the progress bar still fills (it conveys state).
- Touch: 44px minimum, 8px gaps, composer clear of the safe area. Chunky buttons make targets
  comfortably large by default.
- Keyboard: focus rings visible (2px `--primary`), the artifact frame chrome reachable, the
  example chips and "Build it" are real buttons, the streak/gems are non-interactive labels.
- The artifact iframe keeps `sandbox="allow-scripts"` only. The redesign never touches that;
  it is a hard rule.
