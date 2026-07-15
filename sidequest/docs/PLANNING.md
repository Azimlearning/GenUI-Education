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

**Caveat, carry into Phase 1:** the live model path is unverified. No
`ANTHROPIC_API_KEY` was available at Phase 0 close, so the Router and Explainer
have never been exercised against a real Claude response, and no trace row has
been written with real token counts or cost. First Phase 1 task is to run a live
query and confirm the Router returns parseable strict JSON and traces populate.

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

## Phase 1 — Tier 3 Core

**Goal:** real artifacts, no verification yet.

- [ ] Live-model smoke: one real query end to end, Router JSON parses, traces show tokens and cost (carried from Phase 0)
- [ ] Resolve the artifact CSP / opaque-origin conflict (Phase 0 finding 2) before the post-processor injects CSP
- [ ] Router prompt v1 with canonical_concept output, JSON schema validation
- [ ] Artifact Planner node + prompt v1
- [ ] Generator prompt v1: Blocks A to D per spec
- [ ] Write golden example 1: projectile motion (p5.js), hand-polished
- [ ] Write golden example 2: pH explorable (vanilla JS), hand-polished
- [ ] Post-processor v1: fence stripping, CSP injection, vendor path rewrite, error banner wrapper
- [ ] Sandboxed iframe artifact card in frontend (srcdoc, allow-scripts only)
- [ ] Bridge listener: axiom_ready, axiom_event, axiom_error with zod schemas
- [ ] Watchdog: 5s ready timeout swaps to degraded card
- [ ] Verifier stub: logs a report, never blocks (log-only mode)
- [ ] Eval harness v1: Playwright headless render assertions on golden set

**DoD:** 8 of 12 golden queries produce a working interactive artifact rendered in the sandbox.

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
