# Synapse — Codex Community Hackathon KL 2026 Scope Doc

> **Team Dang Wangi** · Track: **Education Access** · Demo Day: **18 July 2026**, Sunway University
> Last updated: 2026-07-13 (scope-review window, 5 days to Demo Day)
>
> This is the working reference for the Codex submission specifically. It captures the problem,
> the plan, and the open decisions — not implementation detail. Companion docs: the full hackathon
> brief lives in [`codex_hackathon_kl_2026_Full_Context.md`](codex_hackathon_kl_2026_Full_Context.md);
> the technical build lives in `../Synapse/`.

---

## 1. Track

**Education Access** — "Learning and literacy tools for multilingual classrooms, students, and
teachers." Direct fit, no stretch required.

---

## 2. Problem Statement

Under the **KBAT curriculum reform**, KSSM SPM science students (Form 4–5 Physics, Chemistry,
Biology) are expected to reason like scientists through hands-on experimentation. But **B40 and
rural schools often lack the equipment, materials, or trained staff to run physical labs.** These
students end up memorising facts from static textbook diagrams instead of building the
experimental intuition the curriculum assumes they already have — widening the gap between
well-resourced urban schools and everyone else.

This is made worse by how students actually try to compensate: they turn to AI chatbots for help,
but a chatbot's output is always flat text. Even a good explanation stays a wall of words — there's
no way to actually *run* the osmosis experiment, drag a concentration slider, and watch a
misconception fail visibly. The output format itself caps how much understanding it can build.

## 3. Objective

Give every Form 4/5 KSSM science student access to a generative-UI AI that turns their question
into a **fully interactive lab experiment** — with guidance and insight, not a wall of text —
regardless of their school's physical lab resources.

## 4. Scope

**Synapse generates interactive lab experiences, not chat answers, for the Form 4–5 KSSM SPM
science syllabus (Physics, Chemistry, Biology).**

- **Decision: ship the fully upgraded app** — not the pared-down 3-component version from the
  original registration doc. Synapse is already substantially further along (all 12 syllabus
  concepts live, teacher dashboard live, learner loop closing) than that early plan assumed, so the
  Codex demo should show the real, current build.

- **The generative UI upgrade (the headline change for this submission):** Synapse's original
  build only ever *selects and arranges* pre-built components — safe and faithful, but bounded to
  what was pre-built. For Codex, the plan is to push this further, **toward the model actually
  generating the interactive itself**, rather than only picking from a fixed catalog.
  - **Decision: land between "the model fills in a structured template" and "the model writes the
    whole thing freely" — closer to the freeform end.** The concept catalog and curriculum-faithful
    guardrails stay (so science accuracy isn't sacrificed), but the interactives themselves become
    much more model-authored and bespoke per question, instead of picking from a fixed prop-filled
    library.
  - **Why this is the ambitious bet:** it's the difference between "smart component picker" and
    "the AI actually designs your lab experiment live" — a much stronger pitch and demo moment, and
    matches where the field is heading (validated by external research: generated interfaces are
    strongly preferred over plain text/chat answers in blind evaluations).
  - **The risk to manage:** more model-authored freedom = more chance of a wrong or ugly render
    live on stage, and slower responses. This needs a safety net (always fall back to a known-good
    component if generation misbehaves) and a rehearsed, not-fully-live demo path for the riskiest
    moments — this is exactly what to pressure-test with mentors this week.

- **Confirm before generating:** like Gemini or ChatGPT, Synapse doesn't silently launch straight
  into a full interactive lab the moment a student asks for one. It first gives a brief
  description of the experiment it's about to build. If the student's own wording already reveals
  a misconception (a contradiction with the real science), Synapse states that contradiction
  plainly right there, before the student confirms. The student then presses **"Generate
  Experiment"** to actually build and load the interactive lab — unless their original prompt
  already explicitly asked to generate the experiment directly, in which case Synapse skips the
  confirmation step and builds it immediately.

- **Demo content:** full current build — all 12 KSSM concepts, three fully faithful flagships
  (osmosis, forces-motion, bonding-electrons) as the anchor of the live walkthrough, teacher
  dashboard, and the learner mastery/spaced-repetition loop — with the upgraded generative
  interactives layered in as the differentiator.

- **Deployment: not yet decided.** Open question for this week: deploy to a public URL so judges
  can access it independently, vs. run live from a laptop with a recorded backup video in case of
  on-site connectivity issues. Needs a decision before Demo Day — flagging as the top logistics
  risk.

---

## 5. Target user / beneficiary

- **Primary:** Malaysian secondary school students (Form 4–5, science stream) preparing for KSSM
  SPM exams, especially in B40 and rural schools without lab access.
- **Secondary:** The science teachers guiding them, who need visibility into what their students
  actually misunderstand (not just their exam scores).

## 6. The idea — Synapse

Synapse is a **visible, agentic pedagogical AI**. It doesn't just answer — it plans, checks, and
builds, and you can watch it do so. The Codex build is a whole new app (a full upgrade, rebuilt
fresh — same name, new engine) with a visible multi-step pipeline:

1. **Plan** — decide what experiment fits the student's question and how to build it.
2. **Check** — verify the student's premise; if their wording contradicts the real science, state
   that contradiction plainly before anything is generated.
3. **Brief & confirm** — describe the experiment to be built; the student presses "Generate
   Experiment" (see §4's confirm-before-generate flow).
4. **Generate** — build the interactive lab itself.
5. **Guide** — respond to the student's interactions with insight and guidance, not just a toy.

The pipeline works in the background to keep every generated experiment pedagogically grounded —
but it's the mechanism, not the headline. The core "wow moment" is simpler: a student asks a
question and watches it become a real, interactive lab, not a wall of text.

Full technical layout: [`codex-technical-spec.md`](codex-technical-spec.md).

---

## 7. Team

**Team Dang Wangi** (as registered with Codex Community Malaysia):

| Name | Role |
|---|---|
| Fakhrul Azim Bin Ahmed Mardzukie (Lead) | AI/ML, prompting/agent workflows, backend |
| Abdul Hafiz Bin Mohd Noor Azman | — |
| Nur Alia Syahira Binti Nor Azam | — |
| Nur Farah Binti Ahmad Nazri | — |
| Por Jie Hao | — |

*(Note: the broader product is also referred to as "Team EduNova" with a larger 7-person roster in
other materials — e.g. the pitch deck and hackAstone submission. For Codex specifically, use
**Dang Wangi**, since that's the registered identity judges will see.)*

In-person attendance at Demo Day (18 July, Sunway University) is confirmed.

---

## 8. Why this fits the judging criteria

| Criterion | Synapse's angle |
|---|---|
| Clarity of Malaysian problem | SPM KSSM syllabus + documented B40/rural lab-access gap — specific, sourced, not generic |
| Usefulness of working demo | Turns a student's question into a runnable interactive experiment — and corrects flawed premises through interaction, not text |
| Product design & workflow | Ask → brief & confirm → interact → observe → understand cycle; visible pipeline reasoning builds trust in *why* |
| Responsible AI | Premise check before generating; science-critical machinery stays pre-built and faithful even as the UI generation gets more expressive; generated code is sandboxed |
| Technical execution | Live generative UI with a tiered generation engine + visible pipeline — a harder, more current technical bet than a static app |
| Marketability & continuation | Planned FYP continuation at UTP; user evaluation studies planned; open-source or SaaS path |
| Presentation quality | Watching a question become a live interactive lab — with the pipeline reasoning visibly on screen — *is* the demo hook |

---

## 9. What to get from mentors this week (12–17 July)

This is the priority list for scope-review sessions:

1. **Feasibility/scope check** — is the "closer to Level 3" generative UI upgrade realistically
   buildable and demo-safe in the remaining days, or should the safety net (fallback to known-good
   components) be the actual headline instead of a backstop?
2. **Pitch & storytelling feedback** — sharpen the framing so the problem, the misconception-fix
   moment, and the generative-UI upgrade land clearly in a short live pitch.
3. **The business side / selling point** — what's the sharpest way to talk about marketability and
   continuation (FYP path, open-source vs. SaaS, who actually pays or adopts this) for the judging
   criterion on marketability?

## 10. Open risks / decisions still needed

- **Deployment:** public URL vs. local-only demo — undecided (see §4).
- **Generative UI safety net:** exact fallback behavior when the model-authored interactive fails
  or renders wrong mid-demo — needs to be nailed down and rehearsed before the 18th.
- **Team identity consistency:** make sure all Codex-facing materials (submission form, deck, demo
  intro) say "Team Dang Wangi," not "EduNova," to match the registration record.
