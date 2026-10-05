# Synapse v4: research, brainstorm, and build plan

> Written 28 September 2026. Working name "v4" for the enhanced version; it is built in place in
> `Synapse-V3/`, not as a new repo (reasoning in section 4.1).
> Inputs: every Synapse build in this repo (v1 `Synapse/`, v2 `synapse-v2/`, v3 `Synapse-V3/`,
> the Level 2 probe `GenUITestV2/`), the GenUI research pass (`research/`), the idea-darwin round
> (`docs/idea-darwin/`), the MCAIT paper and its three reviews (`MCAIT/Paper/`), and a fresh external
> search (section 2). Selection pressure unchanged from 19 Aug: **a complete product for real KSSM
> Form 4/5 students, built solo**. Competitions are not the optimisation target.

---

## 0. The short version

1. **Each build solved one hard problem and dropped the other two.** v1 had the pedagogy (sourced
   misconception diagnosis, learner model) but only 12 hand-built concepts. v2 made generated
   physics safe (a formula DSL with no `eval`, pinned values) but lost bespoke expressiveness. v3
   generates anything and gates delivery on a verifier, but has no pedagogy, no memory, and pays
   90 seconds and ~$0.19 for every question, even repeated ones.
2. **v4 is the merge, organised around a verified syllabus library.** v3's generator and delivery
   gate, v2's declared-physics core as a checkable contract, v1's misconception knowledge base and
   tutor loop, all sitting on the 53-topic KSSM taxonomy and the 1,971 textbook passages already
   ingested but unused.
3. **The biggest gap is evidence, not features.** The full golden set and the hostile set have never
   run, verifier accuracy has never been measured, and no student has used any version. All three
   MCAIT reviewers circled this. Phase A fixes it for about $5.
4. **New since July:** Google shipped teacher-vetted "learning interactives" (17 Sep 2026) with
   agentic solvability checks, and a May 2026 study found **39 to 40% of LLM-generated simulations
   run fine but solve the wrong physics**. Both point the same way: a library of audited labs, and
   verification against a declared contract instead of one model's opinion.
5. **Plan:** A baseline (this week) → B syllabus library → C correctness by contract → D pedagogy
   port → E reach (phone, offline, BM, deploy) → F learner study. Sections 5 and 7.

---

## 1. What the builds proved

### 1.1 The four builds side by side

| | v1 `Synapse/` (1 Jul) | v2 `synapse-v2/` (15 Jul) | v3 `Synapse-V3/` (16 to 18 Jul) | GenUITestV2 (6 Jul) |
|---|---|---|---|---|
| GenUI level | 1: select + configure pre-built components | 2 + escape hatch: model designs a sim as data (Tier B), pinned sims (A), raw HTML (C) | 3: model writes the whole HTML/JS lab | 2: JSON UI spec, fixed vocabulary |
| Safety mechanism | Faithfulness pinned in component code | Restricted expression grammar (`lib/expr.ts`), `when` conditions computed at runtime, pins merged over model output | Structural delivery gate: `artifact_done` needs a type only the verifier can mint; sandbox + CSP + two scan layers | No code executes |
| Pedagogy | Diagnostician against a sourced misconception KB, strategy selection (POE, contrasting cases), tutor loop, spaced repetition, teacher dashboard | Checker flags a wrong premise before building; Guide reacts to slider values | Explainer note only; tutor (Phase 5) not built | None |
| Coverage | 12 concepts, 14 patterns | Anything the sim primitive can express | Anything | Anything shallow |
| Latency | ~seconds | Tier A 3s, Tier B sim ~40s, Tier C 75 to 95s | text 2.6s p50; artifact 60 to 90s typical, 240s worst seen | ~16s |
| Evidence | 12 backend tests, scripted fallback | 118 tests, live runs | 6 runs of a 4-item smoke subset (16 to 17 Jul); verifier caught wrong science twice live | Build + 2 live tests |
| Carry forward | Misconception KB with citations, learner model, POE framing, evaluation plan | `expr.ts` grammar, `when` principle, pins, the "describe what is on screen" helper | Everything: gate, pipeline, evals harness, ML track, UI brand | Proof that a JSON-spec tier is cheap |

### 1.2 Findings

**F1. The three safety strategies are complementary, not rival.** v1 constrains *what can be
shown*, v2 constrains *what can be computed*, v3 constrains *what can be delivered*. The research
pass (`research/generative-ui-research-2026-07-06.md` §2, §8.2) already concluded the strongest
products escalate across levels. No build does that yet.

**F2. Nothing compounds.** Every question is paid in full, including one answered five minutes
earlier (`idea-darwin/round-01.md`). The only compounding pieces are four hand-built "trusted
builtin" labs (`backend/services/builtin_labs.py`: KOH titration, Hooke's law, orbital motion, yeast
fermentation) matched by regex and verified by HTML hash, and a per-browser `localStorage` saved-labs
list (`frontend/lib/labLibrary.ts`). Together these are an accidental prototype of the library, and
they already show the pattern works: audited lab + content hash = a verified lab at zero model cost.

**F3. Almost nothing is measured.** Phase 1 and 2 DoDs are asserted, not measured
(`docs/PLANNING.md`). The hostile set has never run (`MCAIT/Paper/PendingEvaluation.md`). There are no
learner outcomes. The paper's own limitations list (no learner outcomes, verifier not shown correct,
latency high, evaluation preliminary) is the honest backlog.

**F4. The verifier is a single model's judgement.** It caught real errors (ice float: 4 issues,
orbital motion: 3), but its false-pass rate is unknown. External evidence (section 2) says
execution-based checks miss wrong physics 39 to 40% of the time. The render harness only
independently recomputes ground truth for two items (G2, G8; `docs/EVALS.md` §5).

**F5. The curriculum assets are built and idle.** `ml/rag`: 1,971 passages from 17 official KSSM
textbooks (all six subject/form combinations; the four scanned Chemistry experiment books are not
indexed, since there is no OCR). `ml/router-distill`: 53 grounded topics (`kssm_topics.py` v3, each
citing source page), a Keras student at 88.1% domain / 70.4% artifact_type. In production the router
runs in **shadow mode only** (`graph/nodes/router.py:122`); nothing in the live path reads the RAG
index.

**F6. The golden set predates the curriculum grounding.** `evals/golden.yaml` (G1 to G12) was written
as general science, before the taxonomy was corrected, and is not mapped to KSSM chapters. So "golden
pass rate" says nothing yet about syllabus coverage.

**F7. v3 dropped the pedagogy that v1 and v2 had.** No misconception diagnosis, no
predict-observe-explain, no premise check, no learner model. The hackAstone grand-final plan
(`Hackastone/Grand-final/04-prep/grand-final-deliverables.md`) pitches "watch the agents diagnose
and build the simulation", which is v1's diagnosis plus v3's generation. No build does both today.

**F8. Latency has three regimes, and only one is fast.** Library/builtin: instant. v2 Tier B:
~40s. v3 generation: 60 to 90s. Streaming masks the wait but does not remove it (paper limitation 3).
The cheapest speed-up is not generating.

**F9. The product surface assumptions are desktop-first.** A 360px pass exists, but the stimuli
(`idea-darwin/stimuli.md`: phones, metered data, WhatsApp distribution, offline school PCs) say the
phone is the real surface. The UX plan's W1 to W5 are partly done (study note and step strip inside
the titration lab, drag interactions exist) but were written for a demo, not for daily use.

**F10. There is a hard rule already contradicted by shipped code.** CLAUDE.md rule 4 ("no
predefined component library") versus the builtin labs. Unresolved since 19 Aug. The library work sits
directly on it.

**F11. The dev machine cannot run the persistence layer.** No Docker, no Postgres; trace rows have
never been verified (`memory: axiom-dev-environment`). Phase 4 (cache, library, feedback) is
database work. This needs a decision before any Phase B code.

---

## 2. External landscape: what changed since July

| Development | What it is | What it means for Synapse |
|---|---|---|
| **Google "learning interactives"** ([blog, 17 Sep 2026](https://research.google/blog/the-future-of-practice-enabling-teachers-to-create-learning-interactives-with-generative-ui/); [arXiv 2609.20738](https://arxiv.org/abs/2609.20738)) | Teacher picks a curriculum topic, the system proposes learning objectives, Gemini generates game-like simulations with levels, formula toolbox, multi-level hints, worked solutions. "Agentic" auto-evaluation includes **solvability checks that simulate a user and try adversarial extreme parameter values**. Every released interactive is teacher-vetted before entering a library. US pilot: 12 teachers, mean quality 8/10. | Google has validated two things Synapse had deferred: a **vetted library** as the unit of delivery, and **scaffolding** (hints, levels, worked solutions) inside the lab. Synapse's differentiation has to be: student-triggered coverage beyond what a teacher authored, KSSM grounding with page citations, verification by contract, and phone/offline/BM reach. |
| **MAIC-UI** ([arXiv 2604.25806](https://arxiv.org/abs/2604.25806)) | Teacher-authored courseware from textbooks via a generate-verify-optimise pipeline; n=40 lab study; 3-month classroom deployment, pilot +9.21 vs control -2.32. | The bar for "evidence" in this space is now a classroom deployment. Phase F exists because of this. |
| **Neshaei et al., "The Missing Layer"** ([arXiv 2606.15902](https://arxiv.org/abs/2606.15902)) | Position: runtime GenUI cannot be verified at scale, so do generation at design time with instructor review. | The library is the synthesis that answers it: generate at request time for coverage, **promote** to an audited library for scale. Runtime reach, design-time quality. |
| **PDE-grounded intent verification** ([arXiv 2605.09360](https://arxiv.org/abs/2605.09360)) | Reconstructs the governing equations from generated simulation code and scores them against an intended contract. Execution-only repair left **39 to 40% of 220 cases runnable but solving the wrong physics**; contract-guided refinement lifted hard cases by +0.22 to +0.41. | Strongest external argument for section 3's N1: make the physics a declared, checkable object rather than something buried in generated JS. |
| **Kurikulum Persekolahan 2027** ([RTM](https://berita.rtm.gov.my/nasional/senarai-berita-nasional/senarai-artikel/pembaharuan-dalam-kurikulum-sekolah-bermula-sesi-2027/); [summary](https://ecentral.my/kurikulum-persekolahan-2027/)) | New curriculum starts 2027 for Prasekolah, Tahun 1 and Tingkatan 1 only; Tingkatan 2 to 5 stay on the existing (aligned) KSSM. | The 53-topic Form 4/5 taxonomy has a multi-year shelf life. *Inference, not stated in the sources:* the first KP2027 cohort reaches Form 4 around 2030. Content work done now is not wasted next year. |
| **SPM practical tests (Ujian Amali Sains)** ([reported schedule](https://www.bumigemilang.com/jadual-waktu-peperiksaan-spm-2/)) | Reported as scheduled for November 2026 for Biology, Chemistry, Physics. | A concrete, dated student need that matches the original lab-access problem. Supports the "Amali mode" idea (N5). Source is a secondary site; confirm against LPM before relying on dates. |

---

## 3. Brainstorm

### 3.1 The thesis

> **Generate for coverage, verify by contract, promote to a library, teach with the student's own
> misconception.**

Every idea below is judged against it and against the pressure: *would a Form 4/5 student use this
weekly, and does it finish something?*

### 3.2 New ideas (not in idea-darwin round 1)

**N1. Declared-physics core ("the physics contract").** The Planner already emits a
`governing_model`. Make it formal: state variables, step equations, derived quantities, in v2's
restricted expression grammar (`synapse-v2/lib/expr.ts`), plus 3 to 5 metamorphic relations ("double
the mass, the period is unchanged"; "at 45 degrees range is maximal"). A deterministic checker in the
backend evaluates closed-form spot values and the relations *before* any HTML is written. The
Generator then builds the presentation around a vendored evaluator that runs that exact core; it is
not allowed to write its own physics. The verifier's job shrinks to presentation, wiring, and
pedagogy, which is where model judgement is adequate.
*Why it matters:* converts the paper's top limitation ("the verifier is not shown to be correct") into
a measurable property for the checkable subset (most of Physics, much of Chemistry). Directly backed
by the PDE paper.
*Cost:* port the grammar to Python for the checker, vendor a tiny JS runtime under `/vendor/`. Does
not break hard rule 4: it is a maths evaluator, not a component library.

**N2. Verifier mutation testing.** Take the verified labs (the 4 builtins, then library labs), inject
known physics bugs (swap sin/cos, drop a factor of 2, flip a sign, wrong unit), and measure how many
the verifier catches. This is the first ever number for verifier accuracy, costs cents per mutant,
and becomes a permanent regression suite.

**N3. Solvability and fuzz checks in `render_check.py`.** Borrowed from Google: drive each control to
its min, max, and extreme values, check for NaN/Infinity on screen, frozen canvas, runaway values,
and that a success state is reachable. Free once written; catches the "runs at defaults, breaks at the
edges" class.

**N4. Lab promotion ladder.** Every lab has a state: `generated → verified → cached → audited →
canonical`. Rules per state: cached labs evict on a wrong-science flag or low rating; a model or
prompt version bump marks them stale for lazy re-verification; only `audited` labs can be exported,
translated, or shared as canonical. The four builtins enter as `canonical`. This is the answer to
Neshaei et al. and it resolves F10 by definition.

**N5. Amali mode.** KSSM textbooks present experiments as Problem statement / Hypothesis / Variables
(manipulated, responding, fixed) / Procedure / Results (noted in `ml/rag/README.md`). A lab in Amali
mode carries that scaffold: the student states the hypothesis before running, the lab records a
results table from their own runs, and they leave with a filled report skeleton. Timed to the
November practical tests. Seed it from the experiment books already ingested (Biology F4 experiment
book is indexed; the Chemistry ones need OCR).

**N6. Textbook citation on every library lab.** "KSSM Biologi Tingkatan 4, Bab 5, ms. 92", retrieved
from the RAG index at promotion time. Cheap, strongly trust-building for students and teachers, and
it doubles as the curriculum-alignment evidence for X3.

**N7. Misconception-first entry (the v1 port).** Bring `Synapse/backend/app/knowledge/` (sourced
misconceptions: Odom and Barrow on osmosis, Clement and Halloun-Hestenes on force, Taber on bonding,
and so on) into v3 as a retrieval source. When a question matches a known misconception, the plan
gets a predict-observe-explain frame, and predictions resolve by v2's `when` principle: the lab
evaluates the student's answer against its own live state, never against a baked-in answer.

**N8. Device-local learner map.** No accounts (still a non-goal). The syllabus page colours topics
the student has explored and passed a concept check on, stored on the device, with an export code to
move it. v1's learner model and spaced repetition, minus the server. Later, if retention data says
students are lost, add sync.

**N9. Overnight gap filling.** Generate uncovered syllabus topics in off-peak batch runs, audit them
the next morning. The library grows without a student waiting 90 seconds. Use the Batch API for the
discount; check current pricing before sizing the budget.

**N10. Visible checks, not visible agents.** v1's pitch was watching agents think. For a student, what
earns trust is seeing *what was checked*: "Science checked: period matches 2π√(L/g) at 3 lengths;
textbook: Fizik T4 Bab 2." Replaces the generic "Science checked" badge with the actual evidence.

**N11. Audit queue page.** `EVALS.md` §8 already mandates a weekly 15-minute hand audit that has never
happened. Make it a page: next lab to audit, every control to try, pass/fail/flag, and a flag writes a
regression eval automatically (IDEA-0014).

**N12. KSSM concept graph for revision.** Prerequisite edges between the 53 topics (Arcana's
graph tooling could build it). Drives "what to revisit" on the learner map. Parked: nice, not needed
for the first student.

### 3.3 Round-1 ideas, re-read against the new evidence

| Idea (round 1) | Round-1 fitness | Now | Why |
|---|---|---|---|
| X1 zero-cost revision pack / IDEA-0001 syllabus library | 8.7 / 8.5 | **Keep as keystone** | Google's release makes the vetted library the industry pattern, not just a cost trick |
| IDEA-0015 run the deferred evals | 7.7, blocking | **Do first** | Reviewers asked for exactly this; still unrun |
| IDEA-0003 distilled router in production | 7.8 | Keep, after the library | Only pays off in front of a cache |
| X3 curriculum-grounded verifier | 7.5 | **Upgrade** | Combine with N1 and N6: the check becomes contract + citation, not only model judgement |
| IDEA-0013 in-artifact concept check | 7.8 | Merge into N7 | POE with `when` conditions is a better-specified version |
| X2 exam-grounded tutor / IDEA-0007 SPM mode | 7.9 | Keep, after library + N7 | Now also has N5 Amali mode as a sibling |
| X4 forwardable link / IDEA-0008 offline | 7.9 / 7.7 | Keep in Phase E | Free once the library exists |
| IDEA-0009 Bahasa Melayu | 6.4 | Keep, library-only | One-time translation of audited labs, never per request |
| IDEA-0005 tutor loop / IDEA-0006 remix | 6.7 / 6.8 | Phase D | Unchanged |
| IDEA-0011 accounts | 6.0 | Still dormant | N8 covers progress without them |

### 3.4 Considered and rejected

- **A fresh v4 repo.** v3 is the only build with the delivery gate, the evals harness, the ML track,
  and the brand. Rewriting costs weeks and re-opens settled decisions.
- **Going back to v1's component library as the main path.** It caps coverage at what was hand-built,
  which is the problem generation exists to solve. Its *content* (misconceptions) moves; its
  architecture does not.
- **Making v2's Tier B the default renderer.** Safe and 2x faster, but the titration lab (drag, eye
  line, parallax) shows what students need is beyond a shape-scene DSL. N1 takes v2's best idea (the
  maths) without its ceiling (the rendering).
- **Teacher dashboard, payments, native app, collaborative sessions.** Still non-goals.

---

## 4. Target architecture

### 4.1 Where it lives

In `Synapse-V3/`, continuing its phase discipline. v1's knowledge base and v2's expression grammar
are ported in as modules; neither repo is modified.

### 4.2 Request flow

```
question
  │
  ├─► local router (confidence-gated; below threshold → LLM router)
  │
  ├─► library lookup (canonical_concept + KSSM topic)
  │     └─ hit ──► instant lab (<1s) ─► tutor + concept check ─► learner map
  │
  └─ miss
      ├─► text branch: Explainer streams (~2.5s)          [unchanged]
      └─► artifact branch:
            retrieve  : KSSM passage (RAG) + matching misconception (v1 KB)
            plan      : plan + PHYSICS CONTRACT + POE frame + study note + steps
            check     : contract checker (deterministic: spot values + metamorphic relations)
            generate  : HTML shell that runs the vendored core
            postprocess, verifier (presentation, wiring, pedagogy, curriculum)
            render + fuzz check (solvability, extremes)
            DELIVERY GATE ─► student
                         └─► library as `verified` → `cached` → audit queue → `canonical`
```

Hard rules 1 to 3 are unchanged. Rule 4 is restated (decision D1).

### 4.3 Headline metrics (none exists today)

| Metric | Why | Measured from |
|---|---|---|
| Syllabus coverage % (canonical labs / 53 topics) | Is it a resource yet | library table |
| p50 time-to-lab on a covered topic | The daily-use number | traces |
| Cost per student per week | Whether open access is survivable | traces + usage |
| Verifier mutant detection rate | Whether "science checked" is true | N2 suite |
| Hostile block rate (must be 100%, two layers) | Safety claim | hostile set |
| Golden pass@2 on KSSM-mapped items | Capability | golden set |
| Normalised learning gain, two-tier test | Whether anyone learns | Phase F study |

---

## 5. Build plan

Dated from Monday 28 Sep 2026. Solo. Two fixed interruptions: the hackAstone grand final (travel
roughly 27 to 30 Oct; the prep plan freezes its demo build mid-October) and the MCAIT virtual talk
(3 to 5 Nov). API spend estimates use measured costs (~$0.19 per artifact incl. retries in July,
~$0.003 per text-only run) and should be re-checked against current pricing.

### Phase A: baseline and foundations (28 Sep to 4 Oct, ~$5 to 8)

- [ ] Pre-flight per `PendingEvaluation.md`: key valid, backend boots via venv, one smoke item live
- [ ] Run hostile set (under $1), full golden set ($3 to 6), text-only baseline (cents); record to
      `evals/history.jsonl`
- [ ] Map G1 to G12 to KSSM topics; add ~6 KSSM-anchored items so there is at least one per subject/form
- [ ] N2 baseline: 10 to 20 physics mutants of the 4 builtin labs, run the current verifier, record
      detection rate (the "before" number for Phase C)
- [ ] Decisions D1 to D4 (section 7) recorded in `PLANNING.md` and `CLAUDE.md`
- [ ] Storage: SQLite behind the existing SQLAlchemy layer for local, Postgres kept for deploy
      (unblocks Phase B on this machine; resolves F11)

**DoD:** full-run numbers exist; verifier accuracy has a first number; PLANNING.md is current.

### Phase B: syllabus library, i.e. Phase 4 reshaped (5 Oct to 18 Oct, ~$10 to 20)

- [ ] `artifacts` table with `cache_key`, `kssm_topic`, `state` (N4 ladder), `model_version`,
      `prompt_version`, content hash, citation
- [ ] Cache lookup node short-circuits the pipeline on hit (Phase 4 item)
- [ ] Builtins migrate from regex matching to library entries (`canonical`)
- [ ] `/library` page shaped as the syllabus: subject → form → chapter → topic, filled or "build it"
- [ ] Rating + wrong-science flag endpoints; flag evicts; version bump marks stale
- [ ] Seed ~20 high-value topics (the SPM practical experiments first), audit each by hand, promote
- [ ] N6 textbook citation on every canonical lab
- [ ] Shareable lab URL (X4) since it is a cache read

**DoD:** a covered lab opens in under 1s; a flag evicts and the next request regenerates; a Form 4
Physics student can reach a working lab for at least half their chapters without typing.

### Phase C: correctness by contract (19 Oct to 9 Nov, travel excluded, ~$5 to 10)

- [ ] N1: contract schema in the plan, Python checker, vendored JS evaluator, Generator prompt v3
      requiring the core, Verifier prompt narrowed; `make evals` before and after
- [ ] N3: solvability and fuzz assertions in `render_check.py`
- [ ] X3: retrieved KSSM passage into the Verifier; sixth check for notation and scope
- [ ] Re-run N2 mutants; report before vs after
- [ ] Router Phase 4.2: confidence-gated local mode in front of the cache, golden set as the gate

**DoD:** mutant detection rate improves measurably over the Phase A baseline; golden set does not
regress; no Verifier check was weakened (CLAUDE.md).

### Phase D: pedagogy port, i.e. Phase 5 extended (10 Nov to 30 Nov)

- [ ] Port v1 misconception KB (with citations) as a retrieval source; misconception match in the plan
- [ ] POE frame with `when`-evaluated predictions (N7)
- [ ] Tutor loop from bridge events; SPM-style question with marking scheme graded against lab state (X2)
- [ ] Amali mode on library experiments (N5)
- [ ] Remix: "add air resistance" through Planner → contract → Generator → Verifier (Phase 5 DoD)
- [ ] N10 visible checks panel

**DoD:** Phase 5 DoD, plus the three v1 flagships (osmosis, forces and motion, bonding) run
misconception-first end to end on generated labs.

### Phase E: reach (December)

- [ ] Phone-first redesign of the lab takeover and controls (IDEA-0002)
- [ ] Offline: PWA cache of opened labs; chapter pack export for school PCs (M1)
- [ ] Bahasa Melayu for canonical labs only, human-checked
- [ ] N8 device-local learner map
- [ ] Deploy with the M2 policy: library free, new generation rate-limited; cost dashboard from traces
- [ ] N11 audit queue page; flags write regression evals

**DoD:** public URL; cost per student per week and p50 time-to-lab reported from real traffic.

### Phase F: learner study (January onward)

- [ ] Reuse v1's `refdocs/EVALUATION-PLAN.md`: 10 to 15 Form 4/5 students, two-tier diagnostic,
      pre / immediate post / one-week delayed, lab vs text-only condition
- [ ] Ethics/consent through UTP; supervisor involvement per FYP rules

**DoD:** a normalised-gain result, whatever it shows. This is the "future work" the MCAIT paper
promised.

### 5.1 About the grand final

Not the optimisation target, but the calendar overlaps. Phases A and B happen to give a booth what
it most needs: labs that open instantly and do not depend on venue wifi. The pitch's "agents
diagnose" moment is Phase D work and will not exist in a mid-October freeze. Either the pitch
describes diagnosis as the next step, or a narrow bridge is built (the osmosis misconception KB entry
driving one generated lab). That is your call; the plan does not reorder for it.

---

## 6. Risks

1. **The contract (N1) does not fit biology.** Most Biology labs are process explorables, not
   equation systems. Mitigation: the contract is optional per plan; Biology leans on citations (N6),
   the misconception KB, and human audit. Track per-domain mutant detection separately.
2. **Audit time is the real bottleneck.** ~10 minutes per lab, 53 topics, is roughly 9 hours before
   any variants. Mitigation: audit only what gets promoted; seed by SPM practical relevance.
3. **Cached wrong science spreads.** A wrong lab served 100 times is worse than one generated once
   (stimulus S8). Mitigation: eviction on flag is mandatory, and only `canonical` labs are
   shareable or exportable.
4. **Evals show the baseline is worse than believed.** Good: that is the point of Phase A. Replan
   from real numbers rather than defend the old ones.
5. **Scope creep across three ports.** Mitigation: phases keep their DoDs; nothing from v1/v2 is
   ported until the phase that needs it.
6. **Name collision.** A published 2026 paper already uses SYNAPSE for an AI tutor
   (`memory: synapse-naming`). Worth deciding before a public URL and a share link spread the name.

---

## 7. Decisions needed

| # | Decision | Recommendation |
|---|---|---|
| D1 | Restate CLAUDE.md hard rule 4 | "No predefined component library for **generation**. Audited whole labs (the library) and a vetted maths evaluator are allowed." |
| D2 | Phase order: library before tutor, correctness pass inserted as Phase C | Accept; record it in PLANNING.md so rule 5 is followed by explicit decision, not drift |
| D3 | Storage on this machine | SQLite locally, Postgres at deploy, same SQLAlchemy models |
| D4 | Open-access cost ceiling | Library free, new generation rate-limited per session; set a monthly $ cap before deploy |
| D5 | v1 non-goals to promote | Curriculum alignment and Bahasa Melayu in; accounts, payments, teacher dashboard stay out |
| D6 | Name before public launch | Decide before Phase E |

---

## 8. Sources

**Internal:** `Synapse/REPORT.md`, `Synapse/CLAUDE.md`, `Synapse/project-state.md`,
`synapse-v2/README.md`, `GenUITestV2/README.md`, `research/generative-ui-research-2026-07-06.md`,
`Synapse-V3/{README,HANDOFF}.md`, `Synapse-V3/docs/{PLANNING,EVALS,UX_IMPROVEMENT_PLAN,HACKATHON_CONTEXT}.md`,
`Synapse-V3/docs/idea-darwin/*`, `Synapse-V3/ml/{IMPLEMENTATION_PLAN.md,rag/README.md}`,
`Synapse-V3/backend/services/{builtin_labs,local_router}.py`, `Synapse-V3/backend/graph/nodes/router.py`,
`MCAIT/Paper/{ReviewComments,PendingEvaluation,Draft-05-Limitations-Conclusion}.md`,
`MCAIT/Research/Literature-notes/{_Index,MAICUI2026,Neshaei2026-MissingLayer}.md`,
`Hackastone/Grand-final/04-prep/grand-final-deliverables.md`.

**External (accessed 28 Sep 2026):**
- Google Research, [The future of practice: enabling teachers to create learning interactives with generative UI](https://research.google/blog/the-future-of-practice-enabling-teachers-to-create-learning-interactives-with-generative-ui/), 17 Sep 2026
- Kovshov, Choudhury, Iurchenko et al., [Harnessing Generative UI for Education: Tailored Learning Interactives](https://arxiv.org/abs/2609.20738), arXiv 2609.20738, Sep 2026 (abstract only read; full numbers not yet checked)
- [MAIC-UI: Making Interactive Courseware with Generative UI](https://arxiv.org/abs/2604.25806), arXiv 2604.25806
- Neshaei, Shibu, Güreş, [The Missing Layer](https://arxiv.org/abs/2606.15902), arXiv 2606.15902
- [Your Simulation Runs but Solves the Wrong Physics: PDE-Grounded Intent Verification](https://arxiv.org/abs/2605.09360), arXiv 2605.09360
- [Human-AI Collaboration for the Design of Interactive Simulations for Formative Assessment in STEM](https://www.tandfonline.com/doi/full/10.1080/07380569.2026.2712289), Computers in the Schools, 2026 (not yet read)
- RTM, [Pembaharuan dalam kurikulum sekolah bermula sesi 2027](https://berita.rtm.gov.my/nasional/senarai-berita-nasional/senarai-artikel/pembaharuan-dalam-kurikulum-sekolah-bermula-sesi-2027/); eCentral, [Kurikulum Persekolahan 2027](https://ecentral.my/kurikulum-persekolahan-2027/)
- Bumi Gemilang, [Jadual SPM 2026](https://www.bumigemilang.com/jadual-waktu-peperiksaan-spm-2/) (secondary source for practical test timing)
