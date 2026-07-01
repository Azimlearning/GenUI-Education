# Synapse — hackAstone 2026 One-Shot Completion Superprompt

> Paste the fenced block into a fresh Claude Code / agent session opened at `Genui/Synapse/`.
> Goal: take Synapse from the P0 skeleton to a **complete, submission-ready hackAstone 2026 entry**
> — the full product PLUS every enhancement and deliverable that maximises hackAstone's four
> judging dimensions. This is the superset of `refdocs/SUPERPROMPT.md` (which is build-only).

hackAstone context: theme **"Agentic AI for Education"**; UTP is a participating university with a
Steering Committee rep; judged on four EQUAL dimensions — **Innovation & Novelty · Technical
Readiness Level · Commercial Viability · Educational Significance & Applicability**; deliverables
are a **project video (≤8 min)** + a **project description**. Full detail in
`../Hackastone/hackAstone_2026_Full_Context.md`.

---

```
You are completing Synapse for submission to hackAstone 2026 ("Agentic AI for Education"). The P0
skeleton exists in this repo and is verified. Your mission has TWO halves that are equally
weighted: (A) finish the product to a mature, demonstrable state, and (B) produce every
hackAstone-specific enhancement and deliverable. hackAstone scores four dimensions EQUALLY —
optimise all four, not just the code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — LOAD CONTEXT (before writing anything)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Read in order and treat as source-of-truth (they OVERRIDE your assumptions; if two conflict, STOP
and ask):
  1. CLAUDE.md
  2. refdocs/STATUS.md
  3. refdocs/synapse-prd.md
  4. refdocs/concept-catalog.md
  5. refdocs/changelog/DECISIONS.md
  6. refdocs/SUPERPROMPT.md      ← the product build plan (P1–P4). You will EXECUTE this as Part A.
  7. ../Hackastone/hackAstone_2026_Full_Context.md   ← judging criteria + deliverables you serve.
Skim ../Synapse_Demo.html for the visual identity. Before any Claude API code, invoke the
`claude-api` skill to confirm current model ids + the Messages API / streaming / structured-output
shape — do not trust ids from memory.

The 8 non-negotiable constraints in CLAUDE.md apply throughout (agents select-not-generate;
patterns-not-topics; visible streamed reasoning; router with Anthropic-primary; grounded
diagnosis; per-component scientific faithfulness; SSE seam kept in sync; Synapse name + centered
layout). Violating any fails the build.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART A — FINISH THE PRODUCT (execute refdocs/SUPERPROMPT.md)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run its phases in order, flagships-first, with its green gates:
  P1 — one genuinely live vertical slice (osmosis) over Anthropic Claude, real agents, faithful
       gradient-diffusion-sandbox, SQLite learner store.
  P2 — all 12 locked concepts as real, scientifically-faithful interactives (tiers in
       concept-catalog.md).
  P3 — the learner loop closes: interaction events update mastery + spaced repetition; the next
       composition is informed by history.
  P4 — polish + latency (<3s time-to-first-token) + subject theming.
Do not treat Part A as "done" until a real browser click-through of all three flagships works and
`pytest` / `tsc` / `next build` are green. Part B depends on a working product.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART B — hackAstone ENHANCEMENTS, mapped to the four judging dimensions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Build these ON TOP of the finished product. Each bullet names the dimension it scores.

▸ INNOVATION & NOVELTY (originality of concept)
  - Make the multi-agent pipeline unmistakably the star: a polished, animated "reasoning theatre"
    that shows Diagnostician → Strategist → Composer thinking live, with the pedagogical decision
    named on screen ("misconception, not gap → contrasting cases"). This is the thing generic
    GenUI (Gemini dynamic view) structurally hides — foreground it.
  - Add a visible "why THIS component" trace: the Composer explains which pattern it chose and why,
    tied to the strategy. Novelty = pedagogy-driven composition, not topic-matching.
  - Add a short in-app "How Synapse is different" explainer (one screen) contrasting
    select-and-configure GenUI + grounded diagnosis vs one-shot generic UI.

▸ TECHNICAL READINESS LEVEL (build quality, completeness, demonstrable performance)
  - Harden the backend: input validation on /api/ask, structured-output parsing with repair/retry
    (never pass raw model text as props — validate against the registry prop_schema), graceful
    provider fallback (Anthropic→OpenAI→scripted), and a spend/latency log per LLM call.
  - Test coverage: unit tests for each agent's output contract, the router fallback, prop
    validation, and the SSE serialisation; a smoke test per component pattern. Keep pytest green.
  - Observability: log provider, tokens, cost, and time-to-first-token; surface TTFT in a dev panel.
  - DEPLOY it (this is the single biggest TRL signal): containerise the FastAPI backend, deploy the
    Next.js frontend + backend to a public URL (use the vercel skills for the frontend; a small
    host or the Vercel functions/runtime for the backend). Move the learner store to Firebase
    (D-11) for the hosted multi-device demo. Put the live URL in the README.
  - CI: a GitHub Actions workflow running tsc + next build + pytest on push.

▸ COMMERCIAL VIABILITY (market potential, path to adoption)
  - Build a lightweight TEACHER view: a dashboard showing, per student, diagnosed misconceptions,
    mastery per topic, and what's due for review — the B2B2C wedge (schools/teachers adopt it).
  - Write refdocs/GO-TO-MARKET.md: SPM candidate market size (cite the latest official KPM figure,
    don't invent), the B40/rural lab-gap wedge, pricing/adoption path (free tier for students →
    school licences), the FYP→open-source/SaaS continuation plan, and why the pattern library is a
    defensible moat that scales across the full KSSM syllabus.
  - Add a "scales to the whole syllabus" story on-screen: show the 14 patterns already cover 12
    concepts across 3 subjects, and that new topics are config, not new code.

▸ EDUCATIONAL SIGNIFICANCE & APPLICABILITY (pedagogical impact, real deployment)
  - Ground it hard: expand backend/app/knowledge/misconceptions.py with real, SOURCED KSSM/ESL
    science misconceptions for the built concepts, each with a citation. This is the citable
    pedagogical artifact — it is what wins this dimension.
  - Make the learning-science explicit: each strategy the Strategist picks names its technique
    (predict-observe-explain, contrasting cases, worked-example fading, retrieval practice, spaced
    repetition) with a one-line citable rationale.
  - Curriculum alignment: tag every concept with its KSSM/DSKP topic + form; show the alignment in
    the teacher view and the description doc.
  - Bahasa Malaysia: add i18n and a BM interface toggle (at least for the flagship flows) — this is
    a direct access/applicability win for Malaysian classrooms.
  - Accessibility: keyboard-navigable interactives, sufficient contrast, alt text — real deployment
    in real classrooms requires it.
  - Write refdocs/EVALUATION-PLAN.md: a 10–15 participant user-evaluation study design (pre/post
    concept test on the flagship misconceptions, usability measures) — the credible "measurable
    learning outcomes" story. This aligns with the FYP continuation.
  - Responsible AI section: no hallucinated content (select-not-generate), grounded diagnosis,
    human/teacher oversight, data/privacy note for the learner profile.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART C — SUBMISSION DELIVERABLES (hackAstone requires these)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. refdocs/VIDEO-SCRIPT.md — an ≤8-minute project video script + shot-by-shot storyboard.
     Structure: (0:00) the Malaysian problem + user (Form 4/5 SPM, B40 lab gap); (1:00) the wedge
     vs generic GenUI; (1:30) LIVE DEMO — type the osmosis misconception, watch the agents reason,
     the sim contradicts the wrong prediction, the "aha", the tutor loop logs it; (4:30) breadth —
     flash 2–3 more concepts across subjects; (5:30) teacher view + how it scales; (6:30)
     pedagogy + evaluation plan; (7:15) commercial path + team + close. Mark the single strongest
     10 seconds (the osmosis "aha") as the hook.
  2. refdocs/PROJECT-DESCRIPTION.md — the written submission: problem, users, solution, the agentic
     architecture, the four-dimension mapping (explicitly answer each judging criterion), tech
     stack, pedagogy + citations, commercial path, team (Team Dang Wangi, UTP), and the live URL.
     Keep it complete but readable (mirror the tone of the existing refdocs).
  3. Update README.md with the live demo URL, a 30-second "what it is", and run instructions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Plan before non-trivial work (plan + execution docs in refdocs/); log decisions as ADRs in
  refdocs/changelog/DECISIONS.md; update refdocs/STATUS.md and add a CHANGELOG.md entry after
  every phase (CLAUDE.md rules).
- VERIFY BY RUNNING, not reading: pytest + a live /api/ask + real browser click-throughs (use the
  run/verify skills). Report failures honestly with output.
- Keep the SSE seam in sync (schemas.py ↔ types.ts/blocks.ts) whenever you add a pattern.
- Scientific faithfulness is a gate per component (constraint #6) — if you cannot make a sim
  correct, ship a simpler correct version rather than a wrong impressive one, and say so.
- Commit at each green gate with clear messages. Do NOT push unless asked; do NOT commit secrets
  (keys live in backend/.env, git-ignored).
- Prioritise for the four EQUAL dimensions: a working deployed demo + the video + the description +
  the grounded pedagogy beat one more half-built sim. If time is short, protect: (1) the three
  flagships flawless + deployed, (2) the video, (3) the description, (4) the teacher view.

DELIVERABLE: a deployed, working Synapse where a student watches pedagogical agents diagnose them
and compose a faithful interactive; plus a teacher view, grounded pedagogy, a go-to-market and
evaluation plan, and the ≤8-min video script + project description — a submission that scores on
all four hackAstone dimensions. Start with STEP 0, then write the completion plan doc.
```

---

*Notes for the human before you run it:*
- Set a real `ANTHROPIC_API_KEY` in `backend/.env` (and `OPENAI_API_KEY` if you want the fallback live).
- Decide the deploy target (Vercel for the frontend is easiest; the FastAPI backend needs a host — Vercel functions, Fly, Render, or Railway). Tell the agent which, or let it recommend.
- The hackAstone submission date in the context doc (1 July 2026) is for nomination; this superprompt targets a complete, deployed, finals-grade build regardless of that date. Confirm your actual deadline with your UTP advisor.
- Highest-value human step remains: a biology/physics/chemistry person pressure-tests each flagship sim's science before you record the video.
