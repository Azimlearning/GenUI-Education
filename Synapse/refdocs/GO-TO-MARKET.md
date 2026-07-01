# Synapse, Go-to-Market

> hackAstone Commercial Viability. How Synapse reaches real Malaysian classrooms and becomes a
> sustainable product. Figures marked (VERIFY) must be checked against the latest official source
> before the submission or pitch; we do not want to quote a number we cannot defend.

## The market

- **Primary users:** Malaysian KSSM SPM science students, Form 4 and Form 5, across Physics,
  Chemistry, and Biology. The SPM cohort is roughly 380,000 to 400,000 candidates per year
  (VERIFY against the latest Lembaga Peperiksaan / KPM figure). Science-stream candidates are a
  large slice of that.
- **The wedge, B40 and rural lab access.** Faithful practical work (osmosis potato experiments,
  ticker-tape trolleys, titrations, ripple tanks) is exactly what under-resourced and rural
  schools struggle to deliver: no lab time, shared apparatus, large classes. Synapse gives every
  student a scientifically-correct virtual experiment on any device, so the "aha" that normally
  needs a lab happens on a phone.
- **Why now:** SPM has been reformed toward higher-order thinking (KBAT), which rewards conceptual
  understanding over rote recall. Synapse targets exactly the misconceptions that block that
  understanding, with the pedagogy named and grounded.

## The product's defensible moat

The moat is **not** raw generation, where a general-purpose model out-resources any startup. It is
the **faithful, KSSM-aligned component library plus the sourced misconception knowledge base**:

- 14 interaction patterns already cover 12 concepts across all three subjects. New topics are
  **configuration, not new code**, because components are parameterised by interaction pattern,
  not by topic. That is a content-scaling advantage a generic tool cannot copy by prompting.
- The science is pinned in code (constraint #6), so a science-literate teacher can trust it. A
  wrong sim is a trust-killer in education; correctness is the product.
- The misconception KB is a citable pedagogical artifact (see the sources in
  `backend/app/knowledge/misconceptions.py`). It grows with every concept and is hard to
  replicate without the pedagogy work.

## Adoption path

1. **Free tier for students (bottom-up).** Individual SPM students use the student view free. This
   is the growth engine: the osmosis "aha" is shareable and word-of-mouth friendly.
2. **Teacher view drives the wedge (B2B2C).** The `/teacher` dashboard shows, per student, the
   diagnosed misconceptions, mastery per topic, and what is due for review. Teachers adopt it
   because it turns a class of 40 into a readable heatmap of who is stuck on what. Teachers pull
   the tool into the school.
3. **School and district licences (B2B).** Schools pay per-seat or per-cohort for the teacher
   analytics, class management, and BM interface. Tuition centres are a fast second channel.
4. **Ministry / state education department pilots.** The B40 lab-access story aligns with existing
   equity priorities, which is the credible route to scale funding.

## Pricing (initial hypothesis, to be validated)

- **Student free tier:** full student experience, capped usage per day.
- **Student Plus (optional):** low monthly fee (target sensitive to B40 affordability) for
  unlimited use and full progress history.
- **School licence:** per-student annual fee with the teacher dashboard, BM interface, and cohort
  reporting. Volume discount at district scale.
- Keep student access affordable by design; monetise the institution, not the disadvantaged
  student. That is both the ethical and the scalable choice.

## Scale-to-syllabus story (on-screen and in the pitch)

The "How Synapse is different" explainer and this doc make the same point: 14 patterns already
serve 12 concepts across 3 subjects, and covering the rest of the KSSM syllabus is adding
configurations and misconception entries, not rebuilding the app. That is the line that turns a
demo into a company.

## FYP continuation

Synapse doubles as a final-year-project vehicle: the misconception KB and the evaluation study
(see `EVALUATION-PLAN.md`) are publishable, and the pattern-library architecture is a reusable
research contribution. The open-source core plus a hosted SaaS is a realistic path beyond the
hackathon.

## Risks and mitigations

- **Content trust:** mitigated by the code-pinned faithfulness gate and the sourced KB; invite
  subject teachers to pressure-test before wide release.
- **Model cost at scale:** the router uses fast models (Haiku) for the latency-sensitive agents
  and logs per-call cost; the scripted fallback means the product degrades gracefully rather than
  failing when budget is tight.
- **Connectivity in rural areas:** the frontend is light and the components run client-side once
  loaded; an offline-capable build is a natural next step.
