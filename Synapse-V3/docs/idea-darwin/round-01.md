# Round 1 briefing — 19 August 2026

Island: `island.md`. Seeds: `ideas.md`. Stimuli: `stimuli.md`.
Pressure: complete product for real KSSM Form 4/5 students. Solo, heavy push, through late October.
Budget this round: 19 species scored, 3 recommended actions.

## What the round found

The island sorted itself into two groups, and the split is more useful than the ranking.

**Group A: things that change what Synapse is.** X1, IDEA-0001, X4, IDEA-0003. All of them are
about the second student. Today Synapse pays full price, in money and in 90 seconds, for every
question, including one it has answered before. Every other feature is priced on top of that. Fix it
once and the product becomes something a student opens daily instead of something that impresses
once.

**Group B: things that make Synapse better at what it already is.** IDEA-0012 biology reliability,
IDEA-0002 phone-first, X3 curriculum-grounded verification, the Phase 5 tutor and remix work. Real
value, but each one is a linear improvement whose cost stays proportional to usage.

Group A ideas outscored Group B on Value and Cross potential almost uniformly, which is the island
saying the same thing three different ways: the missing piece is not a feature, it is the fact that
nothing compounds yet.

**The strongest single insight of the round:** the library is the multiplier on every other idea on
this list. Bahasa Melayu costs double forever if you translate per request, or a bounded one-time
cost per lab if you translate a library. Human audit of science quality is impossible against
infinite generations and easy against 50 canonical labs. Offline export needs something to export.
Sharing needs something to share. Sequencing the library first is worth more than any individual
feature it makes cheaper.

## Recommended actions

### 1. Run the deferred evaluations before building anything (IDEA-0015)
Roughly $4 to $7, one afternoon. The full golden set and the hostile set have never run. Right now
Phase 1 and Phase 2 are asserted complete rather than measured, which means the next three months of
work has no baseline to be compared against. Do it first or the rest of this plan is unfalsifiable.
`docs/PLANNING.md` already carries the unchecked boxes; `MCAIT/Paper/PendingEvaluation.md` has the
run order and the pre-flight checks.

### 2. Build the syllabus library, not a cache (IDEA-0001 growing into X1)
Phase 4 as written delivers a cache plus a grid of past generations. Build it instead against the
corrected 53-topic KSSM taxonomy in `ml/router-distill/kssm_topics.py`, so the library page is the
syllabus: six subject and form combinations, chapters, covered topics filled, uncovered ones
generating on demand. Same code, one design decision different, and it converts the product from a
question box into a resource with a visible shape and a visible completion percentage.

Definition of done worth aiming at: a Form 4 Physics student can open the app cold and reach a
working lab for any chapter in their syllabus without typing a question.

### 3. Put the distilled router in front of the cache (IDEA-0003)
The Keras student model exists, hits 88.1% on domain, and is doing nothing. In front of a cache it
does not need to be excellent, only confident, because a confident hit skips the LLM entirely and
anything below threshold falls through to the existing router. That is the shadow-mode plus
confidence-gate plan already written in `ml/IMPLEMENTATION_PLAN.md` Phase 4, and the cache is what
makes its 70.4% artifact_type plateau stop mattering.

Together these three give a measurable headline: cost per student per week, and p50 latency on a
covered topic. Neither number currently exists.

## Held for round 2

X2 exam-grounded tutor and IDEA-0007 SPM mode scored 7.9 and are the most interesting product ideas
on the island, but both are far better after the library exists (a tutor on a cached lab is free; a
tutor on a fresh generation is another full round trip). X4 forwardable links becomes nearly free
once the library exists. IDEA-0009 Bahasa Melayu is gated on the same thing.

## Decisions needed

These are yours; the island only recommends.

1. **Phase order.** Recommendations 1 to 3 keep Phase 4 next, which is consistent with PLANNING.md,
   but the library framing pulls curriculum work forward that is not in any phase, and M2
   (cached-only free tier) pulls a Phase 6 rate-limiting decision ahead of Phase 5. CLAUDE.md hard
   rule 5 forbids reordering phases, so this needs an explicit call rather than a silent deviation.

2. **What `builtin_labs.py` is.** Hand-built deterministic labs already ship in
   `backend/services/`, and CLAUDE.md hard rule 4 says no predefined component library. Either
   restate the rule (no predefined components for generation; audited whole labs allowed as cache
   warming) or retire them. The library work sits directly on top of this and should not be built on
   an unresolved contradiction.

3. **Which v1 non-goals get promoted.** "Complete product" implies revisiting the non-goal list.
   Bahasa Melayu and curriculum alignment are the two the island says are now in scope. Accounts,
   teacher dashboards, and payments it recommends leaving dormant.

4. **Cost ceiling for open access.** If the product is meant for real students, a public URL with
   unauthenticated generation is a real exposure. M2 (free cache, rate-limited generation) is the
   cheapest answer, but the ceiling itself is a number only you can set.

## Feeding the island

Append new ideas to `ideas.md` and new environmental pressures to `stimuli.md`, then run another
round. Round 2 should re-score X2, IDEA-0007, and X4 once the library decision is made, since their
feasibility scores are all downstream of it.
