# Synapse — Sources & Research

> Raw research and references behind the design. Lowest authority in the doc order — but the citable grounding for the pedagogy and misconception claims.

---

## Concept origin (this repo)

- `../Adaptive UI for personalized learning_2026-06-04 *.md` — the ideation transcript that fixed the wedge: pedagogy gap + component-quality gap + persistent-learner-model gap vs general-purpose GenUI.
- `../Pre-built component library for KSSM SPM interactive learning_2026-06-05 *.md` — confirmed the by-interaction-pattern library model and the demo-scope discipline.
- `../Synapse_Demo.html` — the clickable mockup: visible agent pipeline + four experience types (osmosis sim, ionic/covalent walkthrough, animal-cell diagram, equation-balancing quick check) across Bio/Chem/Phys. Design tokens (indigo `#3730A3`/`#4F46E5`, teal `#0D9488`) were ported into `frontend/app/globals.css`.
- `../Codex hackathon/codex_hackathon_kl_2026_Full_Context.md` — Codex KL hackathon context (Education Access track, Malaysia-first, Demo Day 18 Jul 2026).
- `../Hackastone/hackAstone_2026_Full_Context.md` — hackAstone context ("Agentic AI for Education", submission 1 Jul, finals Amsterdam Oct 2026).
- `../uiux_team/EDUNOVA/` — the UI/UX team's "TutorLah!" prototype: a sidebar-chat + right visualizer-panel layout with three subject colour themes (Bio green `#cfe4cc`, Chem sand `#e4e4cc`, Physics blue `#ccd9e4`). **Not adopted as the layout** (D-15 — Synapse keeps the centered shape); the **per-subject colour theming** is salvaged for a subtle subject accent.
- `concept-catalog.md` — the 12 locked demo concepts → interaction patterns (the build manifest, D-13).

---

## To gather (P1+)

- [ ] **KSSM SPM syllabus** (Form 4–5 Physics, Chemistry, Biology) — official topic list to ground the registry + misconception KB. Source: KPM / DSKP KSSM documents.
- [ ] **Documented Malaysian/ESL science misconceptions** — literature for osmosis (inverted gradient), bonding, forces, photosynthesis, particle theory. Needed to make the misconception KB citable (ADR-004).
- [ ] **Learning-science techniques** — primary references for: predict-observe-explain, contrasting cases, productive failure, worked-example fading (the expertise-reversal effect), retrieval practice, spaced repetition. These back the *Educational Significance* claim.
- [ ] **GenUI framing** — Google's "dynamic view" / generative-UI material, to sharpen the "we show the machinery they hide" contrast (positioning only, not a dependency).
- [ ] **Sim-fidelity checks** — a subject-expert (biology) pressure-test of the osmosis sandbox's physics before the demo (the one thing a knowledgeable judge will probe).

---

## Reference project (conventions, not code)

- `../../OmniX/` — the project whose documentation/workflow system Synapse mirrors: `CLAUDE.md` operating brief + `refdocs/` with a PRD source-of-truth, `STATUS.md`, and a `changelog/{CHANGELOG,DECISIONS}` + `plans/` + `execution/` structure. Stack borrowed loosely (Next.js + Tailwind + bun on the frontend); the backend is Python here, unlike OmniX.
