# island.md — Synapse v3 evolution island, round 1

Generation 0 (seeds) plus generation 1 (crossbreeds and mutations).
Scoring: Novelty 10%, Feasibility 20%, Value 20%, Logic 20%, Cross potential 10%, Verifiability 20%.
Each dimension is 1 to 10. Fitness is the weighted sum, out of 10.

All scores are relative to the declared pressure: **complete product for real KSSM Form 4/5
students, built solo.** A different pressure produces a different island.

## Scoreboard

| Rank | ID | Species | N | F | V | L | X | Ver | Fitness | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | X1 | Zero-cost revision pack | 8 | 7 | 10 | 9 | 9 | 9 | **8.7** | crossing |
| 2 | IDEA-0001 | Syllabus library (Phase 4 cache, curriculum shaped) | 6 | 7 | 10 | 9 | 9 | 9 | **8.5** | refining |
| 3 | X2 | Exam-grounded tutor | 8 | 6 | 9 | 8 | 9 | 8 | 7.9 | crossing |
| 3 | IDEA-0007 | SPM exam mode | 7 | 7 | 9 | 8 | 8 | 8 | 7.9 | exploring |
| 3 | X4 | Forwardable lab link | 7 | 8 | 8 | 8 | 8 | 8 | 7.9 | crossing |
| 6 | IDEA-0003 | Distilled router in production | 7 | 8 | 6 | 9 | 7 | 9 | 7.8 | refining |
| 6 | IDEA-0013 | In-artifact concept check | 7 | 7 | 8 | 7 | 9 | 9 | 7.8 | exploring |
| 8 | IDEA-0002 | Phone-first lab | 4 | 7 | 9 | 9 | 7 | 8 | 7.7 | exploring |
| 8 | IDEA-0008 | Offline and downloadable | 7 | 8 | 7 | 8 | 8 | 8 | 7.7 | exploring |
| 8 | IDEA-0014 | Quality loop: flags become regression evals | 4 | 8 | 7 | 9 | 7 | 9 | 7.7 | exploring |
| 8 | IDEA-0015 | Run the deferred evaluations | 1 | 9 | 7 | 10 | 4 | 10 | 7.7 | seed, blocking |
| 12 | X3 | Curriculum-grounded verifier | 9 | 5 | 8 | 8 | 8 | 8 | 7.5 | crossing |
| 12 | IDEA-0004 | Curriculum RAG grounding | 8 | 6 | 8 | 8 | 9 | 7 | 7.5 | exploring |
| 14 | IDEA-0012 | Biology reliability | 3 | 7 | 8 | 9 | 5 | 9 | 7.4 | exploring |
| 15 | IDEA-0010 | Deploy, rate limit, cost dashboard | 2 | 7 | 8 | 9 | 5 | 9 | 7.3 | exploring |
| 16 | IDEA-0006 | Remix an existing lab | 5 | 5 | 7 | 8 | 7 | 8 | 6.8 | seed |
| 17 | IDEA-0005 | Tutor loop | 5 | 5 | 9 | 8 | 8 | 5 | 6.7 | seed |
| 18 | IDEA-0009 | Bahasa Melayu | 4 | 6 | 8 | 7 | 6 | 6 | 6.4 | seed, gated |
| 19 | IDEA-0011 | Accounts and progress | 3 | 5 | 7 | 7 | 7 | 6 | 6.0 | dormant recommended |

---

## Generation 1 — crossbreeds

### X1. Zero-cost revision pack
**Parents:** IDEA-0001 x IDEA-0003 x IDEA-0008. **Status:** crossing. **Fitness 8.7.**

**Core question:** what does Synapse cost, and how fast is it, when a student opens a lab that
another student already caused to be built?

Cache lookup keyed on canonical concept, served by the distilled local router with no LLM call in
the path at all, from a library shaped like the KSSM syllabus, exportable as a single self-contained
HTML file the student keeps.

The three parents each solve a piece and none is complete alone. Together, the marginal cost of the
Nth student on a covered topic goes to roughly zero, latency goes from 90 seconds to under one
second, and the product stops being a demo of a pipeline and becomes a revision resource that
happens to have a pipeline behind it.

**Why it scores:** value 10 because it changes the unit economics rather than adding a feature.
Verifiability 9 because every claim is directly measurable (cache hit rate, cost per student per
week, p50 latency on hit, percentage of syllabus covered). Feasibility 7 not 9 because it is three
workstreams, and the Phase 4 cache is a hard prerequisite for two of them.

**Risks:** a cached lab is a lab nobody re-verifies. Eviction on wrong-science flag (IDEA-0014) is
not optional here, it is the safety condition that makes caching acceptable at all.

### X2. Exam-grounded tutor
**Parents:** IDEA-0005 x IDEA-0007 x IDEA-0013. **Status:** crossing. **Fitness 7.9.**

The tutor loop on its own asks pedagogically sound probing questions that a student under SPM
pressure has no incentive to answer. Bind it to the exam instead: after a meaningful interaction
burst, the tutor produces an SPM-format question about the exact system on screen, with a marking
scheme, and grades the attempt against the running simulation state.

This is what turns interaction data into something the student wants. It also gives IDEA-0005 the
verifiability it lacks alone (5 on its own, 8 in the cross), because marking-scheme agreement is
checkable where "was that a good probing question" is not.

### X3. Curriculum-grounded verifier
**Parents:** IDEA-0004 x the existing Verifier. **Status:** crossing. **Fitness 7.5.**

The verifier currently checks whether the science is right. It does not check whether the science is
the science this student is examined on. Feed the retrieved KSSM passage into the verifier context
and add a sixth check: notation, terminology, and scope match the syllabus for that form.

Highest novelty on the island (9). It is a claim nobody in the literature base has made: correctness
and curriculum alignment are different verification targets, and a generative learning system needs
both. Feasibility 5 because RAG quality is unproven in the live path and this touches the one
component that must never regress.

### X4. Forwardable lab link
**Parents:** IDEA-0008 x IDEA-0002, mutated by S3 (WhatsApp) and S4 (locked school networks).
**Status:** crossing. **Fitness 7.9.**

A lab is already a single self-contained HTML document. Give it a stable short URL and a
"send to a friend" action, and distribution runs on the channel Malaysian students already use, with
no login, no install, and no app store. Opening a shared link costs one cache read.

The cheapest growth mechanism available, and essentially free once X1 exists, because a shared link
is just a cache hit from a different entry point.

---

## Generation 1 — mutations

### M1. Chapter pack for a school PC
**Stimulus:** S4 + S5. Derived from IDEA-0008.
A whole chapter's labs as one downloadable folder a teacher copies onto offline school machines. No
account, no network, no per-student cost. Not scored this round; carried to round 2 because it
depends entirely on X1 existing first.

### M2. Cached-only free tier
**Stimulus:** S6 plus the cost exposure in IDEA-0010.
Unauthenticated users get the library and cache hits for free; only generation of a genuinely new
concept is rate limited. Makes an open public URL financially survivable without adding accounts.
Folds into IDEA-0010 as an implementation policy rather than competing with it.

---

## Generation 0 — notable seed cards

### IDEA-0001. Syllabus library
**Status:** refining. **Fitness 8.5.** **Children:** X1.

Phase 4 of PLANNING.md, but shaped by the corrected 53-topic KSSM taxonomy in `ml/router-distill`
rather than by whatever users happen to ask. The library page is not a list of past generations, it
is the syllabus, with covered topics filled and uncovered ones generating on demand.

The keystone species. Almost everything downstream gets cheaper once it exists: translation becomes
a one-time cost per lab instead of per query (IDEA-0009), human audit becomes possible at all
(IDEA-0012), offline export has something to export (IDEA-0008), sharing has something to share
(X4). This is why it outranks ideas with higher immediate visible impact.

**Unresolved tension:** `backend/services/builtin_labs.py` already ships hand-built deterministic
labs, which sits awkwardly against CLAUDE.md hard rule 4. Either the rule gets restated as "no
predefined component library for generation" with audited whole labs allowed as cache warming, or
the builtin labs get retired. Decide before building on top of them.

### IDEA-0015. Run the deferred evaluations
**Status:** seed, blocking. **Fitness 7.7.**

Not an improvement, a prerequisite. The full 12-item golden set has never run and the hostile set
has never run at all, so Phase 1 and Phase 2 definitions of done are asserted rather than measured,
and there is no baseline against which any later work can be shown to have helped. Roughly $4 to $7.
Logic 10 and verifiability 10 because it is definitionally the thing that produces evidence.

### IDEA-0002. Phone-first lab
**Status:** exploring. **Fitness 7.7.**

A 360px pass exists. That is not the same as designing the lab takeover, the controls, and the drag
interactions for a thumb on a six-inch screen as the primary case, with desktop as the widened
variant. Given the stated user (B40 and rural Form 4/5), the phone is the product surface and the
desktop is the demo surface.

### IDEA-0009. Bahasa Melayu
**Status:** seed, gated. **Fitness 6.4.**

Genuinely important for the stated audience, and deliberately held one round, because sequencing
changes its cost by an order of magnitude. Translating at request time doubles generation cost
forever. Translating cached library labs is a one-time cost per lab, auditable by a human, and
reusable. Do it after IDEA-0001, not before.

### IDEA-0011. Accounts and progress
**Status:** dormant recommended.

An explicit v1 non-goal, and S3 says the distribution model is forwarded links rather than logins.
Revisit only if retention data from a deployed build says anonymous sessions are actually losing
students. Your call: the island only recommends.
