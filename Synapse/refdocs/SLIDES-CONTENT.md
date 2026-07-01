# Synapse — Slide Content (Detailed)

> Copy-paste source for the deck. Five sections: Background, Problem, Objective, Solution, How It
> Works. Grounded in `PROJECT-DESCRIPTION.md`, `GO-TO-MARKET.md`, `synapse-prd.md`,
> `concept-catalog.md`, `EVALUATION-PLAN.md`. Figures marked **(VERIFY)** must be checked against
> the latest official source before the submission or pitch.

---

## 1. Project Background — and why it matters for Malaysia now

**Title:** A curriculum reform meets an access gap

**1.1 — The curriculum has changed, but the classroom hasn't caught up**
Malaysia's SPM science curriculum (KSSM) has moved toward **KBAT** (Kemahiran Berfikir Aras Tinggi
/ higher-order thinking skills). Where older exams rewarded recall — define a term, state a law —
KBAT questions ask students to *apply*, *analyse*, and *predict* in novel scenarios. A student can
no longer pass by memorising; they have to actually hold the right mental model of how something
works.

**1.2 — That reform quietly assumes something: real practical work**
The place students build a correct mental model isn't the textbook, it's the lab: watching a
potato strip actually shrink in salt water, pulling an actual ticker tape through a trolley
experiment, titrating an actual acid into an actual base, watching an actual ripple tank. KBAT's
premise is that students have had enough hands-on contact with the phenomenon to reason about it
when the question is unfamiliar.

**1.3 — But lab access is not equal across Malaysian schools**
B40 and rural schools are exactly where this assumption breaks down:
- Shared or missing apparatus — one set of glassware for a class of 40.
- Large class sizes that turn "practical" into "watch the teacher demonstrate once."
- Limited lab timetable slots, especially where a school serves multiple form levels.
- Roughly 380,000–400,000 students sit for SPM each year **(VERIFY** against the latest Lembaga
  Peperiksaan Malaysia / KPM figure**)**, with science-stream candidates forming a large share of
  that cohort — this is a national-scale gap, not a niche one.

**1.4 — Why this is the moment to act**
Two forces are converging: (a) the exam now explicitly rewards conceptual understanding via KBAT,
and (b) generative AI has matured enough to deliver a faithful, interactive experiment on a phone —
which is the device most students actually have, even where a lab is not available. Synapse sits
precisely at that intersection: it doesn't just explain the concept, it recreates the "aha" moment
the lab was supposed to deliver, on whatever device the student already owns.

---

## 2. Identified Problem

**Title:** Students can recite the answer and still hold the wrong idea

**2.1 — The core problem: durable misconceptions, not lack of information**
Science education research (and the KSSM classroom reality) shows students frequently carry
**specific, well-documented misconceptions** even after being taught the correct answer:
- **Osmosis:** students believe water moves toward "more water" (a naive concentration-equalising
  intuition), rather than moving down a water-potential gradient toward the region of *higher
  solute* concentration. (Sourced misconception: `osmosis-inverted-gradient`, grounded in Odom &
  Barrow's diffusion-osmosis diagnostic literature.)
- **Forces & motion:** students believe a moving object needs a *constant force* to keep moving —
  an Aristotelian intuition — rather than Newton's first law (an object in motion stays in motion
  unless acted on by a net force). (Sourced misconception: `newton-force-needed-to-keep-moving`,
  grounded in Clement and Halloun–Hestenes force-concept research.)
- **Bonding & electrons:** students conflate ionic and covalent bonding, missing that electrons are
  *transferred* (metal + non-metal) versus *shared* (non-metal + non-metal). (Sourced
  misconception: `bonding-sharing-vs-transfer`, grounded in Taber's chemical-bonding research.)
- Similar documented misconceptions exist for photosynthesis (Driver) and circuits (Shipstone),
  extending the pattern across all three subjects.

**2.2 — Why this is invisible to normal teaching and testing**
A student can pass a recall-based quiz — state the definition of osmosis correctly — while the
model in their head is still wrong. The wrong model only resurfaces when a KBAT-style question asks
them to *apply* it to an unfamiliar scenario. That means:
- Standard formative assessment doesn't catch it (right answer, wrong reason).
- Teachers with 40-student classes have no scalable way to probe *which* misconception each
  individual student holds.
- The misconception then persists into the exam itself, where KBAT is specifically designed to
  expose it.

**2.3 — The resource that would fix this is the hardest one to access**
The textbook remedy for a misconception is a *contradicting experience* — predict, observe, get
proven wrong, then re-explain. That is exactly the hands-on practical work described in the
Background section, and exactly what B40/rural schools cannot reliably deliver at scale.

**2.4 — Existing AI/EdTech tools don't close this gap either**
- **Generic GenUI / "AI tutor" tools** generate an explanation or even a UI one-shot from a prompt.
  That's a real risk in a science context: a hallucinated simulation (wrong physics, wrong
  chemistry) is worse than no simulation, because a student can't tell it's wrong.
- **Static content platforms** (videos, worksheets, chatbots that just answer questions) never
  diagnose *which* misconception is driving a wrong answer — they treat every wrong answer as a
  knowledge gap to be re-explained, when often it's a specific, nameable misconception that needs a
  specific intervention (contrasting cases), not a repeated lecture.

---

## 3. Objective

**Title:** Diagnose the specific misconception, then intervene the right way — visibly

**3.1 — Give every student equal access to the "aha" moment**
Regardless of whether their school has a working lab, every Malaysian SPM science student should be
able to run a **scientifically faithful virtual experiment** that surfaces their specific
misconception and corrects it — not a generic explanation, not a hallucinated simulation, on any
device they already have.

**3.2 — Make the diagnosis grounded, not guessed**
Match the student's response against an explicit, sourced, KSSM-aligned misconception knowledge
base (with citations — Odom & Barrow, Clement, Halloun-Hestenes, Taber, Driver, Shipstone), so the
system classifies into a known, named misconception rather than the AI improvising a guess about
what the student might be thinking.

**3.3 — Make the intervention pedagogically correct, not one-size-fits-all**
Different diagnoses need different fixes. The objective is to distinguish:
- a **misconception** (needs contrasting cases — show the wrong model failing against the right
  model side-by-side),
- a **knowledge gap** (needs worked-example fading — scaffolded explanation, gradually removed),
- a **mastery check** (needs retrieval practice — a quick quiz, not more teaching),

and to actually apply the matching learning-science technique, naming it explicitly rather than
defaulting to "explain again."

**3.4 — Make the reasoning visible, to both student and teacher**
Show the diagnosis → strategy → composed experiment chain live, streamed as it happens, so:
- students see *why* they're being given this particular interactive, which builds trust and
  metacognitive awareness of their own misconception;
- teachers can watch (or later review via the teacher dashboard) exactly what was diagnosed and
  why, turning a black-box "AI tutor" into an auditable pedagogical decision.

**3.5 — Make it measurable, not just plausible**
Pair the product with a concrete evaluation design (see `EVALUATION-PLAN.md`): a two-tier pre/post
diagnostic (answer + reason) on the three flagship misconceptions, with an immediate and
one-week-delayed post-test, so the claim "this fixes the misconception" is something the team can
actually demonstrate with data, not just assert.

---

## 4. Proposed Solution

**Title:** Synapse — a visible multi-agent tutor that composes, not generates

**4.1 — The core architectural choice: select-and-configure, never generate-from-scratch**
Synapse's defining decision is that its agents never generate UI or scientific content freehand.
They **select** a component from a pre-built, KSSM-faithful library and **configure** its
parameters. This eliminates the single biggest risk in AI-for-science-education — a hallucinated
simulation that looks convincing but is scientifically wrong — because every component's science is
pinned in code and reviewed once, not regenerated per request.

**4.2 — The four-agent pipeline (the pipeline itself is the product)**

| Agent | Role | Reads | Writes |
|---|---|---|---|
| **Diagnostician** | Classifies the student's response against the sourced misconception KB | question + learner profile + misconception library | a diagnosis: misconception / knowledge gap / mastery check |
| **Pedagogy Strategist** | Chooses the matching learning-science intervention | the diagnosis | a strategy (contrasting cases / predict-observe-explain / worked-example fading / retrieval practice) + target interaction pattern |
| **Component Composer** | Selects and configures a faithful interactive component | the strategy + the component registry | a typed, validated component block (never raw markup) |
| **Tutor Loop** | Watches the interaction, updates the learner's mastery model, schedules spaced repetition | interaction events | an updated learner profile that informs the *next* session |

**4.3 — The moat: 14 patterns already covering 12+ concepts across 3 subjects**
Rather than building one bespoke simulation per topic, the library is parameterised by
**interaction pattern**, not by topic — e.g. a single `gradient-diffusion-sandbox` pattern already
serves osmosis, and the same *kind* of pattern generalises to other diffusion/gradient phenomena.
Concretely, the current library spans:
- Biology: osmosis (`gradient-diffusion-sandbox`), cell division (`stage-sequencer`), the menstrual
  cycle (`process-timeline`), the digestive system (`labelled-diagram-explorer` +
  `matching-pairs`), genetics (`punnett-square-builder`), the nervous system
  (`signal-pathway-sim`).
- Chemistry: reactions (`reaction-lab-sandbox`), bonding & electrons
  (`electron-bonding-explorer`), atomic structure (`atomic-structure-explorer`).
- Physics: forces & motion (`force-motion-sim`), electricity (`circuit-builder-sandbox`), waves &
  optics (`wave-optics-sandbox`).
- Cross-cutting: `quick-check-quiz` for retrieval practice on any topic.

Because new topics are added as **configuration, not new code**, covering more of the KSSM syllabus
scales without rebuilding the app — a content-scaling advantage a generic prompt-a-UI competitor
cannot copy by prompting harder.

**4.4 — Reliability by design**
All model calls run through a config-driven **provider router** — Anthropic Claude as the live
primary (Haiku for the latency-sensitive Diagnostician/Composer, Sonnet for the Strategist), with
OpenAI as fallback, and scripted logic as a last resort. The system degrades gracefully rather than
failing outright if a provider is unavailable or a budget cap is hit — important for a tool meant to
work reliably in real classrooms, not just in a demo.

---

## 5. How the Solution Works

**Title:** From a student's answer to a live, correct experiment — reasoning shown at every step

**5.1 — Step 1: the student engages with a question**
The student is presented with a question inside a topic (e.g. an osmosis scenario: "a potato strip
is left in salt water — what happens to it, and why?"). This is deliberately a KBAT-style
application question, not a recall question, so it's capable of surfacing a misconception rather
than just testing memorisation.

**5.2 — Step 2: the Diagnostician classifies the response, live**
The Diagnostician reads the student's answer plus their learner profile (past mastery, past
misconceptions) and matches it against the sourced KSSM misconception knowledge base. Its
diagnosis streams to the screen as it's produced — e.g. "This matches
`osmosis-inverted-gradient`: the student believes water moves toward 'more water' rather than down
a water-potential gradient." The diagnosis is a classification into a known, citable entry, never
an improvised guess.

**5.3 — Step 3: the Pedagogy Strategist picks and names the intervention**
Given "misconception" (rather than "knowledge gap" or "mastery check"), the Strategist selects the
matching learning-science technique — here, **contrasting cases**: put the student's predicted
(wrong) outcome directly against the true outcome so the contradiction is unmissable. This choice,
and the reasoning behind it, is also shown on screen, not hidden.

**5.4 — Step 4: the Component Composer selects and configures the experiment**
The Composer takes the strategy ("contrasting cases" for an osmosis misconception) and picks the
matching component from the pre-built library — here, `gradient-diffusion-sandbox`, configured with
`cell_mode: 'plant-cell'` so the student sees a real plant cell go turgid or plasmolysed depending on
solute concentration. It outputs a typed, schema-validated block (pattern + props), never raw
generated markup or freehand science.

**5.5 — Step 5: the frontend renders the composed interactive live**
The whole chain — Diagnostician → Strategist → Composer — streams to the browser over Server-Sent
Events (SSE) as it happens. The student and teacher watch the reasoning unfold in real time; the
interactive itself appears as the final, validated step, not a black-box finished page. In the
osmosis example, this is a predict-observe-explain flow: the student commits a prediction, runs the
sandbox, and sees whether their prediction held.

**5.6 — Step 6: the Tutor Loop closes the loop**
The interaction (was the prediction right, how the student responded, which misconception was
targeted) is logged, the learner's mastery model is updated, and a spaced-repetition review is
scheduled. The *next* session is already informed by this one — if the misconception resurfaces
later, the system already knows to check for it.

**5.7 — Reliability underneath it all**
Every model call in this chain goes through the provider router described in the Solution section,
so if the primary provider is unavailable, the system falls back rather than breaking mid-session —
critical for something meant to run reliably in a live classroom, not just a controlled demo.

---

*Source docs: `PROJECT-DESCRIPTION.md`, `GO-TO-MARKET.md`, `synapse-prd.md`, `concept-catalog.md`,
`EVALUATION-PLAN.md`.*
*Figures marked (VERIFY) need checking against the latest official SPM candidate statistics before
the pitch/submission.*
