# UX Improvement Plan (demo-focused)

Goal: shift Axiom from "chat with a small quiet widget attached" to "ask one
question, then a colorful, interactive study-lab takes over the screen." This
plan is written for a time-boxed hackathon push: ruthlessly prioritized, with
a demo-critical path first and the science-correctness guardrail kept intact.

## 1. What actually caused the current feel ("what caused this issue")

The complaints trace to a few specific, fixable decisions, not a vague quality
problem:

1. **The artifact looks muted because the Generator prompt tells it to.**
   `backend/prompts/generator.md` Block C literally says: "dark-friendly
   neutral palette... one restrained accent... The artifact should look like a
   quiet instrument, not a website." The two worked examples in Block D are
   deliberately minimal and grey-green. The prompt even states the examples
   "dominate output quality more than any instruction" — so the muted,
   text-forward look is baked into the single highest-leverage part of the
   system. This is the root cause of "too much text, not colorful, not
   infographic, not attractive."

2. **The study note lives in the chat, separate from the artifact.** The
   Explainer streams an 80-140 word note into the chat column; the artifact is
   a separate object. So the learner reads text in one place and interacts in
   another. You want the note + steps folded INTO the artifact. Nothing in the
   plan schema currently carries a "study note" or "experiment steps" field
   for the artifact to render, so the generator has nothing structured to lay
   out.

3. **The artifact is a side panel, not the answer.** The shell already has a
   3-pane layout (`StudyRail | chat | LabPane`), which is good, but the
   artifact sits in a ~1.1fr side column at roughly a third of the width. Your
   vision is the opposite: after a prompt, the lab takes ~80% and the chat
   recedes. The layout exists; the emphasis is wrong.

4. **Shell and artifact now clash.** The shell was already restyled to
   study-vibes (green/gold, serif, `study-card`, `study-badge` in
   `globals.css`). The artifact inside the iframe is still the old "quiet
   instrument." They no longer match, which makes the whole thing feel
   half-finished.

5. **Ask/answer loop.** Standard chat transcript. The fix is not to remove
   chat but to make the artifact the star and let the transcript be a thin
   history, so each turn feels like "run an experiment," not "send a message."

Already partly done (don't redo): Explainer is already trimmed to 80-140 words
(v2); `interaction_mode: drag_drop` already exists in `schemas/plan.py`, the
planner, and the generator prompt; the 3-pane shell and study theme exist.

## 2. Target experience (restating your vision precisely)

- Center column: the familiar text input. Ask a question there.
- On submit: the lab region expands to ~80% of the screen and shows a genuine
  lazy-loading state (the staged pipeline: designing -> building -> checking
  the science -> polishing), not a dead spinner.
- The output is the whole interactive UI: colorful, infographic, study-vibes.
- Top of the lab always shows subject + type (biology / experiment, etc.).
- The quick study note and, for experiments, the step list live INSIDE the
  generated UI, not as separate chat text.
- Experiments are genuinely drag-and-drop (drag material/tool onto the bench,
  run, measure), not slider-only.

## 3. Workstreams, prioritized

Impact = visible demo difference. Effort = rough build time. Risk = chance of
breaking the science-correctness guarantee (the thing that must not regress).

### W1. Generator restyle: colorful, infographic, note-inside (HIGHEST leverage)
Impact: very high. Effort: medium. Risk: medium (eval regression).

- Rewrite Block C style rules: from "quiet neutral instrument" to a defined
  vibrant-but-accessible study palette (multiple accent colors, colored stat
  tiles/cards, clear visual hierarchy, big readable type). Keep contrast/
  accessibility and the dark base so it matches the shell.
- Rewrite BOTH golden examples in Block D to be the new quality bar: colorful,
  infographic, with an in-artifact "study note" panel and (for the experiment
  example) a visible step list. This is the single most important change; the
  examples dominate output.
- Add an explicit "layout regions" instruction: title + subject badge row, a
  colored study-note card, the interactive stage, controls, and (experiments)
  a numbered steps strip.
- Guardrail: re-run `make evals-smoke` before/after; science checks must still
  pass. Never weaken the Verifier to make a pretty artifact pass.

### W2. Lab-takeover layout + real lazy-loading (HIGH visible impact)
Impact: high. Effort: medium. Risk: low (frontend only).

- After submit with an artifact coming, expand the LabPane to dominate (~80%
  on desktop; full-screen with a back affordance on mobile). Chat collapses to
  a slim strip / history drawer.
- Turn the existing `ProgressStages` into a full-pane skeleton that fills the
  lab area while building, so the takeover feels intentional, not empty.
- Keep the subject + type badges pinned at the top of the lab (already present
  in `LabPane` header and `StreamRenderer`).

### W3. Structured study-note + steps in the plan (MEDIUM, makes W1 reliable)
Impact: medium. Effort: medium. Risk: low-medium.

- Add to `ArtifactPlan`: `study_note: str` (a 2-3 line scannable takeaway) and
  `steps: list[str]` (present for experiments; the procedure the learner
  follows). Length-capped like the other fields.
- Update the Planner prompt to produce them; update the Generator prompt to
  render them as the in-artifact note card and steps strip.
- This makes W1's "note inside the artifact" reliable and consistent instead
  of improvised per generation. Do W1 first (fast visible win), then W3 to
  harden it.

### W4. Drag-and-drop reliability for experiments (MEDIUM)
Impact: medium (you called it out explicitly). Effort: medium. Risk: medium.

- The plumbing exists (`interaction_mode: drag_drop`). What's missing: the
  Planner reliably choosing it for `virtual_experiment`, a drag-drop GOLDEN
  EXAMPLE in Block D (so the generator has a concrete pattern), and a Verifier
  check that the drop actually changes scientific state (not a decorative
  drag). Add a pointer-events based example (works on touch), not desktop
  HTML5 drag.

### W5. Less text in the chat column (LOW effort, supports "too much text")
Impact: medium. Effort: low. Risk: low.

- Once the note lives in the artifact (W1/W3), reduce the chat to a one-line
  hook + the "open lab" affordance, or fold the note entirely into the lab so
  the transcript is just questions and thumbnails. Explainer is already short;
  this is mostly a frontend de-emphasis.

## 4. Recommended demo-critical path (do in this order)

1. **W2 layout takeover + full-pane lazy-loading.** Pure frontend, low risk,
   instantly makes the product feel like "the lab is the answer." Safe first
   win.
2. **W1 generator restyle + rewritten golden examples.** The big visible
   change to color/infographic/vibe. Gate it behind a smoke-eval run so
   science doesn't regress.
3. **W5 chat de-emphasis.** Cheap, completes the "less text" ask.
4. **W3 structured note/steps**, then **W4 drag-drop example**, if time allows.

W1 and W2 together deliver ~80% of the visible difference. W3/W4 harden it.

## 5. Non-negotiable guardrails

- No unverified artifact reaches the client; the Verifier stays authoritative.
  A prettier prompt does not get to bypass or weaken a science check
  (CLAUDE.md hard rule 1-2).
- Every Generator or Verifier prompt edit re-runs the smoke evals before it is
  considered done, and the delta is recorded (CLAUDE.md: "run make evals
  before and after; never weaken a Verifier check to make an eval pass").
- Sandbox rules unchanged: `sandbox="allow-scripts"` only, `/vendor/*` local
  libraries only, no runtime CDN. Colorful does not mean new dependencies.
- Colorful must stay accessible: keep contrast high, respect reduced-motion,
  keep 44px touch targets. Infographic, not unreadable.

## 6. Explicitly out of scope for this push

ML Phase 4 (router distillation into production) is parked. Cache/library,
tutor loop, and auth remain out of scope. This push is purely about the
generated output's look and the lab-first layout.
