# Synapse, Evaluation Plan

> hackAstone Educational Significance. A concrete, credible study design for measuring whether
> Synapse actually improves conceptual understanding. Sized for a hackathon-to-FYP timeline
> (10 to 15 participants), with a clear path to a larger study.

## Research question

Does a single Synapse session (diagnose, predict-observe-explain with a faithful interactive,
grounded explanation) produce a measurable gain in conceptual understanding of the targeted
misconception, compared to the student's pre-session understanding?

## Design

A within-subjects pre/post design on the flagship misconceptions, with a small control comparison.

- **Participants:** 10 to 15 Form 4 or Form 5 science students. Recruit for a mix of prior
  attainment; include B40 and rural students where possible, since they are the priority users.
- **Targeted concepts:** the three flagships, because their science is fully faithful:
  osmosis (osmosis-inverted-gradient), forces and motion (newton-force-needed-to-keep-moving),
  and bonding (bonding-sharing-vs-transfer).
- **Instrument:** a short two-tier diagnostic test (answer plus reason) built on the flagship
  misconceptions. Two-tier items separate "right answer, wrong reason" from genuine
  understanding, which is exactly what we claim to fix. The osmosis items can adapt the
  Odom and Barrow diffusion-osmosis diagnostic.

## Procedure

1. **Pre-test** (10 min): the two-tier diagnostic on all three concepts.
2. **Intervention** (about 20 min): each student works through the Synapse session for each
   flagship, committing a prediction before running each sim.
3. **Immediate post-test** (10 min): a parallel form of the diagnostic.
4. **Delayed post-test** (1 week later, 10 min): the same parallel form, to test retention. This
   is where the spaced-repetition scheduling should show its value.
5. **Usability measures:** a short System Usability Scale (SUS) plus two open questions ("what
   helped most", "what was confusing"). Capture time-to-first-token and completion informally to
   sanity-check latency.

## Measures and analysis

- **Primary outcome:** proportion of two-tier items answered with the correct answer AND correct
  reason, pre vs post. Report normalised gain per concept.
- **Retention:** immediate vs delayed post-test scores.
- **Process signal:** the platform already logs each prediction as an interaction event and
  updates mastery; export that as a secondary, objective measure of in-session learning.
- **Analysis:** paired comparison (Wilcoxon signed-rank given the small n) on pre vs post; report
  effect size and individual trajectories rather than over-claiming significance at this n.
- **Qualitative:** thematic summary of the open responses, especially where the "aha" landed.

## Small control comparison

Where feasible, split participants: half do the full predict-observe-explain Synapse session, half
read a correct static explanation of the same concept (no prediction, no interactive). The
contrast isolates the value of the pedagogy (commit-then-contradict) over simply being told the
right answer.

## Success criteria

- A positive normalised gain on the two-tier items for the flagship misconceptions.
- Retention at one week that is not fully lost, ideally supported by the review scheduling.
- SUS in the acceptable range and qualitative evidence that students noticed the moment their
  prediction was contradicted.

## Threats to validity and mitigations

- **Small sample:** treat results as a pilot; report per-student trajectories; pre-register the
  larger study.
- **Test-retest practice effects:** use parallel forms and the delayed post-test.
- **Novelty effect:** the delayed post-test and the control comparison guard against "it worked
  because it was new and interactive."
- **Faithfulness dependency:** only evaluate concepts whose sims are fully faithful (the three
  flagships), so we are measuring the pedagogy, not a shaky simulation.

## Path to a larger study (FYP)

Scale to 60 or more students across two or three schools, add a proper control group, extend to
more concepts as their sims reach full faithfulness, and connect the mastery and spaced-repetition
data to longitudinal outcomes. The misconception KB and the two-tier instrument are the
publishable core.
