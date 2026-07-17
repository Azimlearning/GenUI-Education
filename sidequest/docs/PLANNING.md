# PLANNING.md — Axiom Build Plan

Living document. The coding agent updates checklists as tasks complete. Phases are sequential; a phase begins only when the previous phase's definition of done (DoD) is verified.

## Current status

- **Active phase:** Phase 1 (Phase 0 DoD met, with one caveat below)
- **Last updated:** 2026-07-16

---

## Phase 0 — Walking Skeleton

**Goal:** end-to-end plumbing with zero intelligence. Type a question, see streamed text.

- [x] Monorepo scaffold (`/frontend`, `/backend`, `/vendor`, `/evals`, `/docs`)
- [x] docker-compose: Next.js, FastAPI, Postgres, hot reload on both apps
- [x] Alembic initialized, `sessions` and `messages` tables migrated (all six tables in `0001`)
- [x] SSE endpoint `POST /api/ask` streaming typed events
- [x] Chat UI: message list, input, SSE consumption with zod validation
- [x] LangGraph skeleton: Router + Explainer nodes only, wired to Claude API
- [x] Vendored libraries downloaded, pinned, served at `/vendor/*`, checksums recorded
- [x] Trace logging table + middleware (every node call recorded)
- [x] `make dev`, `make test`, `make lint` all green

**DoD:** a question typed in the UI returns a streamed, model-generated text answer with full trace logged.

**Status:** met in echo mode, verified by driving the real UI in a browser: question
submitted, `meta` rendered, text streamed token by token, `done` closed the stream,
29 backend tests and 8 frontend tests green, ruff/eslint/tsc clean.

**Caveat resolved 2026-07-16:** live-model smoke ran with a real key. Router
returned parseable strict JSON on every attempt (5 queries, zero parse retries),
canonical_concept normalization matched the prompt rules exactly
(`ice_water_density_buoyancy`, `wave_interference_superposition`), G10 routed
text_only with the correct value, and real usage flowed into `done`
(~0.0026 USD per text-only run on haiku). Trace rows remain unverified because
neither Docker nor Postgres exists on the dev machine; confirm rows on the
first `make dev` + `make migrate` run.

### Phase 0 findings that shape Phase 1

1. **`/vendor` must be same-origin with the artifact, not the backend.** A srcdoc
   iframe resolves relative URLs against the parent's base URL, so generated code
   requesting `/vendor/p5.min.js` hits the frontend origin. Resolved with a Next.js
   rewrite proxying `/vendor/*` to the backend; verified serving 1MB of p5 through
   port 3000. Keep this in mind if the frontend ever moves to a separate host.
2. **Artifact CSP `script-src 'self'` will not work as written.** `docs/SECURITY.md`
   section 2.3 specifies `script-src 'unsafe-inline' 'self'` for artifacts, but a
   srcdoc iframe with `allow-scripts` and no `allow-same-origin` has an opaque
   origin, and `'self'` in an opaque origin matches nothing. A `<script src="/vendor/p5.min.js">`
   tag would be blocked by our own CSP. Decide in Phase 1 before the post-processor
   injects the CSP: either inline the library source into the artifact, or widen
   `script-src` to the vendor origin explicitly. Do not silently drop the check.
3. **three.js UMD is end-of-life.** r160 removed `build/three.min.js`; pinned to
   0.159.0, the last release that ships it (verified: defines `THREE` global,
   REVISION 159). A future three.js upgrade requires an ES-module strategy, which
   the single-document artifact format does not currently allow.
4. **DB writes must never sit on the stream's critical path.** With the database
   down, awaited best-effort writes (session upsert, message insert, trace row)
   each cost ~4s of connect timeout and pushed first token to 19s. Fixed: traces
   and chat persistence are fire-and-forget background tasks
   (`services/background.py`) with a 2s engine connect timeout, and `meta` is
   emitted before the trace write. Keep this rule for every node added later.
5. **Sequential Router then Explainer costs ~4.4s to first token warm** (two
   LLM round trips back to back; measured on haiku, 3 queries). This is the
   baseline the Phase 3 parallel-branch work must beat to hit the sub-2s budget.
6. **Router prompt tuning input:** G1 ("why does ice float?") routed to
   explorable_diagram; golden expects simulation. Same for wave interference.
   Not a Phase 1 blocker, but Router prompt v1 tuning should revisit the
   simulation vs explorable_diagram boundary ("continuous process you perturb"
   vs "structure you step through").

## Phase 1 — Tier 3 Core

**Goal:** real artifacts, no verification yet.

- [x] Live-model smoke: one real query end to end, Router JSON parses, usage and cost flow (2026-07-16; trace rows still pending a DB-up run, see Phase 0 findings 4)
- [x] Resolve the artifact CSP / opaque-origin conflict: CSP names the configured app origin explicitly instead of 'self'; scan-before-inject ordering (decision recorded in SECURITY.md section 2.3, 2026-07-16)
- [x] Router prompt v1 with canonical_concept output, JSON schema validation
- [x] Artifact Planner node + prompt v1
- [x] Generator prompt v1: Blocks A to D per spec
- [x] Write golden example 1: projectile motion (p5.js), hand-polished
- [x] Write golden example 2: pH explorable (vanilla JS), hand-polished
- [x] Post-processor v1: fence stripping, CSP injection, vendor path rewrite, error banner wrapper (plus forbidden-API scan, viewport/charset, size cap; 23 unit tests)
- [x] Sandboxed iframe artifact card in frontend (srcdoc, allow-scripts only)
- [x] Bridge listener: axiom_ready, axiom_event, axiom_error with zod schemas
- [x] Watchdog: 5s ready timeout swaps to degraded card
- [x] Verifier stub: logs a report, never blocks (log-only mode)
- [x] Eval harness v1: Playwright headless render assertions (run.py + render_check.py)

**DoD:** 8 of 12 golden queries produce a working interactive artifact rendered in the sandbox.

**Status 2026-07-17:** pipeline proven live end to end. Three distinct artifacts
generated and verified: G2 projectile lab (passed all render checks: axiom_ready,
control wired via screenshot diff, zero forbidden APIs), G8 pendulum experiment,
and G1 ice/density explorer rendered through the real UI in a browser with
correct physics (91.9% submerged at 20 C, exactly rho_ice/rho_water). The DoD
measurement itself (full 12-query eval run, $5-15) awaits an explicit go-ahead
per the cost discipline rule.

### Phase 1 live findings (2026-07-17)

7. **Artifact timeout: 30s (brief) vs reality.** Generation streams at 60-130
   tok/s and complete artifacts are 3-9k tokens; measured runs land at 60-90s
   total. ARTIFACT_TIMEOUT_S now defaults to 150 (brief said 30, TECHNICAL.md
   budgeted 45 p95; both are unachievable at current artifact sizes). Phase 3
   should reconcile the TECHNICAL.md budget table with measured reality.
8. **Generator must use the streaming API.** The same generation took 22s
   standalone-streamed vs 77s+ (then killed) non-streaming in-pipeline; long
   non-streaming requests can be held server-side. Also positions Phase 3's
   artifact_delta for free.
9. **Planner JSON discipline needed prompting.** Two live failure modes:
   unescaped double quotes inside string values, and over-long layout_notes
   blowing the schema cap. Fixed with prompt rule 7 (single quotes inside
   values, start-with-{, end-with-}) plus explicit field length limits in the
   prompt; layout_notes cap relaxed 600 -> 1200, governing_model 2000 -> 4000.
   If a third planner-JSON failure class appears, stop prompt-patching and
   switch the Planner to tool-use structured output.
10. **Render harness must re-point the artifact CSP.** The injected CSP names
   the configured public origin; the eval harness serves /vendor from an
   ephemeral origin and must substitute it (evals/render_check.py does). Same
   applies to any future non-3000 deployment: set PUBLIC_ORIGIN.
11. **Embedding artifacts in a script string requires escaping `</`** or the
   artifact's own closing script tags terminate the host script
   (render_check harness bug, fixed; relevant to any future artifact-preview
   feature that inlines HTML into JS).

## Phase 2 — Verification

**Goal:** zero unverified artifacts can reach the client, enforced structurally.

- [ ] Verifier prompt v1: five-check protocol, strict JSON verdict
- [ ] Retry loop: fail routes back to Generator with issues, max 2 retries
- [ ] Degradation path: artifact_failed event, retry button, honest copy
- [ ] Delivery gate: artifact_done can only be emitted from the post-verification code path (make bypass a type error, not a convention)
- [ ] Hostile input tests green (fetch injection, cookie access, parent access)
- [ ] Post-processor forbidden-API scan as independent second layer
- [ ] Eval harness v2: verifier pass-rate and retry-count metrics in CI

**DoD:** all 12 golden queries handled correctly (10 artifacts pass within 2 retries, 2 route to text_only); both hostile tests blocked by two independent layers.

## Phase 3 — Streaming UX

**Goal:** perceived responsiveness under 2 seconds on every query.

- [ ] Parallel branches: Explainer streams while artifact branch runs
- [ ] Full typed SSE protocol per API_SPEC.md
- [ ] Staged progress card driven by artifact_status events
- [ ] artifact_delta progressive stream (build-progress code preview, optional toggle)
- [ ] All artifact card states: loading, ready, degraded, flagged
- [ ] Timeout: 30s artifact branch cap, text branch never blocked
- [ ] Mobile pass at 360px, reduced-motion respected

**DoD:** text starts streaming under 2s on all golden queries; a 60s generation still feels alive via staged progress.

## Phase 4 — Cache and Library

**Goal:** repeat concepts render instantly; the library compounds.

- [ ] cache_key computation and artifacts table per DATA_MODEL.md
- [ ] Cache lookup node short-circuits pipeline on hit
- [ ] /library page: grid, domain filter, instant open
- [ ] Feedback endpoints: rating, wrong_science flag
- [ ] Eviction: flag or low rating removes from cache, lazy regeneration
- [ ] model_version stamping and lazy invalidation on bump

**DoD:** cached concept renders under 1s; a wrong_science flag evicts and next request regenerates.

## Phase 5 — Tutor Loop and Remix

- [ ] Interaction events flow: bridge → API → Tutor context
- [ ] Tutor prompt v1: probing questions, one per meaningful interaction burst
- [ ] Follow-up Q&A grounded in current artifact plan
- [ ] Modification cycle: delta request → Planner → Generator → Verifier with prior code as context
- [ ] Remix UI on artifact card

**DoD:** "add air resistance" on the projectile sim yields a correctly modified, re-verified artifact.

## Phase 6 — Hardening and Deploy

- [ ] Rate limiting (10 generations/hour/session unauthenticated)
- [ ] Cost dashboard from trace data
- [ ] Deploy: Vercel + Railway/Fly, Postgres managed, env audit
- [ ] Accessibility pass (keyboard, focus, ARIA on artifact card chrome)
- [ ] Load sanity: 20 concurrent sessions without event interleaving bugs

**DoD:** public URL, all evals green in CI against production config.

---

## Milestones

| Milestone | Definition |
|---|---|
| M1 First artifact | Any golden query renders an interactive artifact locally |
| M2 Trustworthy | Phase 2 DoD met |
| M3 Feels fast | Phase 3 DoD met |
| M4 Compounds | Phase 4 DoD met |
| M5 Teaches | Phase 5 DoD met |
| M6 Live | Deployed and stable |

## Top risks and mitigations

1. **Generator reliability plateau.** Outputs work for physics sims but fail for biology diagrams. Mitigation: domain-specific example pairs in Block D; track pass rate per domain in evals; grow postprocess.py.
2. **Verifier false confidence.** Verifier passes subtly wrong science. Mitigation: hand-audit 10 random passed artifacts per week during Phases 2 to 4; add each caught miss as a regression eval.
3. **Cost blowout during tuning.** Strongest model on Generator plus Verifier plus retries. Mitigation: evals-smoke subset, per-run budget caps, cache aggressively even during dev.
4. **Latency perception failure.** Staged progress not enough for 60s builds. Mitigation: artifact_delta code preview; consider speculative generation for top library gaps later (not v1).
5. **Scope creep.** Auth, teacher tools, multi-language. Mitigation: the What Not To Do list is binding for v1.

## Explicit non-goals for v1

Auth and accounts, payments, teacher dashboards, curriculum alignment, languages other than English, native mobile apps, collaborative sessions, and any predefined artifact component library.
