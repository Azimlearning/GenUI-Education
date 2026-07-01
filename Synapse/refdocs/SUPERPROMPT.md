# Synapse — One-Shot Build Superprompt

> Paste the block below into a fresh Claude Code / agent session opened at `Genui/Synapse/`.
> It assumes the P0 skeleton already exists and is verified (see `refdocs/STATUS.md`). It drives
> the build from P0 → a demo-ready product covering the 12 locked concepts, flagships-first.

---

```
You are building Synapse — a visible multi-agent pedagogical platform for Malaysian KSSM SPM
science (Form 4–5 Physics · Chemistry · Biology). The P0 skeleton is already in this repo and
verified working. Your job is to take it to a demo-ready product in one focused run.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — LOAD CONTEXT (do this before writing any code)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Read, in order: CLAUDE.md → refdocs/STATUS.md → refdocs/synapse-prd.md →
refdocs/concept-catalog.md → refdocs/changelog/DECISIONS.md. These are the source of truth and
they OVERRIDE any assumption you'd otherwise make. If any two disagree, STOP and ask — do not
resolve silently (CLAUDE.md order-of-authority). Skim ../Synapse_Demo.html for the visual
identity you must match.

Before writing any code that calls the Claude API, invoke the `claude-api` skill to confirm the
exact current model ids, the Messages API shape, streaming, and structured-output patterns. Do
not trust model ids from memory — the config placeholders (`claude-haiku-4-5-20251001`,
`claude-sonnet-5`) must be verified/corrected against that skill.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NON-NEGOTIABLE CONSTRAINTS (from CLAUDE.md — violating these fails the build)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Agents SELECT + CONFIGURE pre-built components; they NEVER generate UI/markup from scratch.
   The LLM outputs a component `pattern` + validated `props` — nothing else renders.
2. The component library is parameterised BY INTERACTION PATTERN, not by topic (14 patterns
   cover the 12 concepts — see concept-catalog.md).
3. Agent reasoning is STREAMED and VISIBLE (SSE `agent_step` events) — the pipeline is the demo.
   Never collapse it into a silent finished page.
4. All LLM calls go through the Provider Router. Anthropic Claude is the live primary
   (Haiku: Diagnostician + Composer; Sonnet: Strategist); OpenAI is the fallback. Keys are
   server-side only (backend/.env) — never in the Next.js client, never NEXT_PUBLIC_.
5. Diagnosis is GROUNDED in backend/app/knowledge/misconceptions.py — the model classifies into
   that list; it does not invent misconceptions. Expand the KB with sourced KSSM misconceptions
   as you build each concept.
6. Faithfulness is per-component non-negotiable: a concept is "live" ONLY when its science is
   correct (water moves toward higher solute; ΣF=ma; V=IR; Snell's law; correct meiosis halving;
   amylase→starch; etc.). A wrong sim is worse than no sim — a science-literate judge will probe.
7. Keep the SSE seam in sync: backend/app/models/schemas.py ↔ frontend/lib/types.ts +
   frontend/lib/blocks.ts. A new pattern means a registry entry (backend) AND a component +
   map entry (frontend), added together (D-10).
8. Product name is Synapse; keep the CENTERED layout from Synapse_Demo.html (the UI/UX team's
   sidebar "TutorLah!" prototype is NOT adopted). Salvage only the per-subject colour theming
   (Bio green, Chem sand, Physics blue) as a subtle accent keyed off the composed block's subject.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUILD ORDER (flagships first — never build the second of anything until the first is green E2E)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE P1 — one genuinely live vertical slice (OSMOSIS), end to end:
  a. Implement the OpenAI fallback adapter in providers/router.py (mirror the Anthropic one).
  b. Flip the four agents (backend/app/agents/*.py) from scripted to LLM-driven via
     `get_router().run(agent=..., prompt=..., system=...)`, with structured output:
       - Diagnostician → returns a Diagnosis (kind + subject/form/topic + misconception_id from
         the KB). Ground it: pass the candidate misconceptions for the detected topic in the prompt.
       - Pedagogy Strategist → returns a Strategy (technique + target_pattern + rationale).
       - Component Composer → returns validated `props` for the chosen pattern (validate against
         the registry prop_schema; reject/repair invalid props — never pass raw model text through).
       - Tutor Loop → stays deterministic (writes to the learner store).
     Keep each agent's scripted logic as the fallback path when the router raises
     ProviderUnavailable, so the demo still runs with no API key.
  c. Build the FAITHFUL gradient-diffusion-sandbox React component (predict → drag slider → run →
     water visibly moves toward higher solute, contradicting the misconception → "aha"). Replace
     the P0 placeholder. Wire props from the streamed block.
  d. Verify E2E in a real browser: type the osmosis misconception → watch the 4 agents stream →
     the live sim renders and behaves correctly → the tutor-loop write appears. Fix what the
     browser surfaces (SSR-OK-but-client-crash bugs, etc.).
  e. Swap the in-memory learner store for SQLite (store/learner_store.py — add a SqliteLearnerStore
     behind the same interface; select via the LEARNER_STORE env var).
  GATE: bunx tsc --noEmit clean, bun run build clean, backend pytest green, one full live
  browser run of osmosis working. Only then proceed.

PHASE P2 — the remaining 11 concepts, in the tiers from concept-catalog.md:
  Tier 1 (finish flagships): electron-bonding-explorer (Chem), force-motion-sim (Phys).
  Tier 2: stage-sequencer, circuit-builder-sandbox, atomic-structure-explorer.
  Tier 3: process-timeline, punnett-square-builder, signal-pathway-sim,
          labelled-diagram-explorer (+ matching-pairs), wave-optics-sandbox, reaction-lab-sandbox.
  For EACH concept: (1) add/confirm its registry entry + prop_schema; (2) add sourced
  misconceptions to the KB where relevant; (3) build the faithful React component + add it to
  LIBRARY in frontend/lib/blocks.ts; (4) make the Composer able to emit it; (5) browser-verify
  the science is correct. Update refdocs/STATUS.md's per-concept checklist after each.

PHASE P3 — learner model closes the loop: interaction events (predictions, slider values, quiz
  answers) POST back from the component → Tutor Loop updates mastery + schedules spaced
  repetition → the next composition is informed by it. Surface "due for review" on the profile.

PHASE P4 — polish + demo: subject colour theming; latency < 3s time-to-first-token (streaming);
  an 8-minute demo beat sheet (osmosis misconception is the opening "aha"). Add a scenario chip
  per subject flagship on the landing page.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPONENT QUALITY BAR (every interactive)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Predict-observe-explain where the pattern supports it: make the student commit BEFORE revealing.
- Scientifically faithful (constraint #6). Encode the correct rules; do not fake the physics.
- Hydrated purely from the streamed `props`; no hard-coded topic logic inside the component.
- Accessible + clean; match the Synapse indigo/teal identity (frontend/app/globals.css tokens).
- Emits interaction events for the Tutor Loop (P3).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Plan before non-trivial work: write a plan doc + execution doc in refdocs/plans and
  refdocs/execution (CLAUDE.md rule 2). Log new decisions as ADRs in DECISIONS.md.
- After every phase: update refdocs/STATUS.md and add a refdocs/changelog/CHANGELOG.md entry.
- Verify by RUNNING, not by reading: backend `pytest` + a live `POST /api/ask`; frontend
  `bunx tsc --noEmit` + `bun run build` + a real browser click-through (use the run/verify
  skills). Report what actually happened, including failures.
- Do the cheapest/most-faithful/most-visible-reasoning thing when a spec is ambiguous; log it.
- Commit at each green gate with a clear message. Do not push unless asked.

DELIVERABLE: a running Synapse where a student asks a question, watches the four agents reason
live, and gets a scientifically-faithful interactive composed for them — across all 12 concepts,
with the three flagships flawless. Start by reading the docs in STEP 0 and writing the P1 plan.
```

---

*Tune before pasting:* if you want a hosted multi-device demo, add "use Firebase for the learner
store (D-11)" to P1e. If time is tight, tell it to stop after P1 + Tier-1 flagships and ship those.
