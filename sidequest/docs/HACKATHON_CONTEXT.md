# HACKATHON_CONTEXT.md - Codex Community Hackathon KL 2026

Synced from `../../Codex hackathon/` (the sibling folder at the `Genui` repo root: `codex_hackathon_kl_2026_Full_Context.md`, `codex-project-scope.md`, `codex-technical-spec.md`). Those files are the source of truth for event logistics and are not duplicated here in full; this doc pulls the parts that matter for how Axiom gets built and pitched.

## How Axiom fits in

"Axiom" is this repo's internal engineering codename. Externally, the product this repo builds is **Synapse**, continuing the same lineage as the Codex hackathon submission:

- **Synapse (v1)** - the original `../Synapse/` monorepo: LangGraph agents (Diagnostician, Pedagogy Strategist, Component Composer, Tutor Loop) selecting from a pre-built component library. This is the project registered with Codex Community Malaysia in the original application.
- **Synapse v2** - `../synapse-v2/`, a standalone Next.js app built in four days to satisfy `codex-technical-spec.md` under deadline pressure (no backend, no persistence, tiered generation ladder A/B/C). Its own README is explicit that it is a scope-cut stand-in: "The spec called for a Python backend; with four days and no backend written, one service in one language removes a deploy, a CORS surface, and a class of demo-day failures."
- **Axiom (this repo, "Synapse v3")** - the real, non-time-boxed build: FastAPI + LangGraph + Postgres backend, a Verifier gate that structurally prevents unverified artifacts from reaching the client, and a parallel ML track (router-distill classifier, curriculum RAG) grounded in the actual KSSM Form 4/5 Bio/Chem/Physics syllabus. This is where the "generative UI lab experiment" idea gets built properly rather than under a demo deadline.

When the hackathon docs say "Synapse," read it as this lineage. When they describe `synapse-v2`'s tiered architecture (Tier A/B/C, single Next.js service), that describes the fallback build, not Axiom's own architecture (see `SYSTEM_ARCHITECTURE.md` for Axiom's actual pipeline).

## Event essentials

- **Event:** Codex Community Hackathon KL 2026, "Raising the Floor: AI for Malaysia Boleh"
- **Organiser:** Codex Community Malaysia (codexhackathon.my)
- **Format:** selected cohort, up to 150 builders; online prep 11-17 July, in-person Demo Day 18 July 2026 at Sunway University, Petaling Jaya
- **Track:** Education Access ("learning and literacy tools for multilingual classrooms, students, and teachers")
- **Prizes:** 1st USD 15,000 / 2nd USD 10,000 / 3rd USD 5,000 in Codex platform credits; top 5 teams get 12 months ChatGPT Pro

**Flag: today's date is 2026-07-18, which is Demo Day per this schedule.** If that is accurate, this is the day of the in-person judged presentation at Sunway University, not a build day. Worth confirming with the user before treating this as a normal working session.

## Team Dang Wangi (registration record)

| Name | Role |
|---|---|
| Fakhrul Azim Bin Ahmed Mardzukie (Lead) | AI/ML, prompting/agent workflows, backend |
| Abdul Hafiz Bin Mohd Noor Azman | - |
| Nur Alia Syahira Binti Nor Azam | - |
| Nur Farah Binti Ahmad Nazri | - |
| Por Jie Hao | - |

Use "Team Dang Wangi" on all Codex-facing materials, not "EduNova" (a name used in other pitch materials for the broader product with a larger roster).

## The problem this is pitched against

Malaysian Form 4-5 KSSM SPM science students (Physics, Chemistry, Biology), particularly in B40 and rural schools without functioning physical labs, end up memorising static textbook diagrams instead of building experimental intuition. Generic AI chatbots compensate with more text, which caps how much understanding a wall of words can build. The pitch is: turn a student's question into a runnable interactive lab experiment instead of a chat answer.

## Judging criteria (7 dimensions)

1. Clarity of Malaysian problem and user
2. Usefulness of the working demo
3. Product design and user workflow
4. Responsible AI implementation
5. Technical execution with Codex (the AI coding tool)
6. Marketability and continuation potential
7. Final presentation quality

Axiom's hard rules already map onto criterion 4 directly: the Verifier gate, `sandbox="allow-scripts"` only, no runtime CDN fetches. Worth keeping in mind when writing the demo script, since "responsible AI" is a scored dimension, not just an engineering nicety.

## Open decisions inherited from the scope doc

These were still open as of `codex-project-scope.md` (last updated 2026-07-13) and may now be moot if Demo Day has already happened, but are recorded here in case they still apply to Axiom's own launch plan:

- **Deployment:** public URL judges can access independently, vs. local laptop demo with a recorded backup video for connectivity risk. Undecided in the source doc.
- **Confirm-before-generate flow:** Synapse (all versions) is meant to describe the experiment and get a "Generate Experiment" confirmation before building, unless the prompt already explicitly asked to generate, in which case the confirmation is skipped. Check whether Axiom's current pipeline (`docs/SYSTEM_ARCHITECTURE.md`) implements this gate, since it's part of the product pitch, not just synapse-v2.
- **Post-hackathon intent:** continuation as the lead's FYP at UTP, user evaluation studies (10-15 participants), possible open-source or SaaS path. Relevant to how Axiom's `PLANNING.md` roadmap gets framed beyond the hackathon.

## Source documents

Full detail lives in the sibling folder, not copied here in full to avoid drift:

- `../../Codex hackathon/codex_hackathon_kl_2026_Full_Context.md` - event rules, timeline, prizes, full team record
- `../../Codex hackathon/codex-project-scope.md` - problem statement, scope decisions, open risks
- `../../Codex hackathon/codex-technical-spec.md` - synapse-v2's technical architecture (the fallback build, not Axiom's own)
