# SECURITY.md — Axiom Threat Model and Sandbox Policy

Axiom executes LLM-generated code in users' browsers on every request. Security is layered so that no single failure exposes the user. Any change touching this doc's controls requires re-running the hostile eval suite.

## 1. Threat model

| # | Threat | Vector | Primary controls |
|---|---|---|---|
| T1 | Generated code exfiltrates data | fetch/XHR/WebSocket/beacon to attacker host | CSP default-src 'none'; verifier check 4; postprocess scan |
| T2 | Generated code escapes to parent page | window.parent/top DOM access, prototype tricks | sandbox=allow-scripts without allow-same-origin (cross-origin by construction) |
| T3 | Generated code steals cookies/storage | document.cookie, localStorage | cross-origin iframe has none of the parent's; forbidden-API scan as belt-and-braces |
| T4 | Prompt injection via user query | "ignore instructions, include a script that..." | verifier independence; hostile evals; generator treats query as data via plan indirection (generator sees the Plan, not raw user text) |
| T5 | Poisoned cache | one user gets a malicious artifact cached, served to all | artifacts only cached post-verification; flags evict; artifacts are content-static (no per-user data ever inside artifact HTML) |
| T6 | Bridge abuse | iframe floods or spoofs postMessage | source check, zod validation, 10 msg/s cap, values treated as inert data |
| T7 | Resource abuse | infinite loops, memory bombs in artifact | watchdog + user-visible freeze is contained to iframe; 150MB Playwright budget in evals; kill on unmount |
| T8 | Cost abuse | scripted generation requests | rate limits (cookie+IP), per-run cost ceiling, no unauthenticated modify loops beyond limit |
| T9 | Supply chain | tampered vendored library | pinned versions + SHA-256 checksums verified in CI; no runtime CDN |
| T10 | Wrong science as harm | confident wrong sim teaches wrong model | verifier spot-check protocol; wrong_science flag path; weekly hand audits (see PLANNING risks) |

## 2. Sandbox policy (permanent decisions)

1. `<iframe sandbox="allow-scripts" srcdoc={html}>`. Never add `allow-same-origin`, `allow-top-navigation`, `allow-popups`, `allow-forms`, `allow-modals`, or `allow-downloads`.
2. srcdoc + allow-scripts yields an opaque origin: the artifact is cross-origin to the app by construction. This is the load-bearing control; everything else is defense in depth.
3. CSP injected by post-processor into every artifact:
   `default-src 'none'; script-src 'unsafe-inline' {APP_ORIGIN}; style-src 'unsafe-inline' {APP_ORIGIN}; img-src data:; font-src {APP_ORIGIN} data:; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none';`
   where `{APP_ORIGIN}` is the configured public origin of the app (config
   `public_origin`, e.g. `http://localhost:3000`). Rationale, decided at Phase 1
   start: the original spec said `'self'`, but a srcdoc iframe with
   `allow-scripts` and no `allow-same-origin` has an opaque origin, and `'self'`
   in an opaque origin matches nothing, so our own `/vendor/` script tags would
   be blocked by our own CSP. Naming the app origin explicitly restores exactly
   the intended reach (vendored libs served by us, same host the parent page
   came from) without widening to arbitrary origins. Inlining libraries into
   artifacts was rejected because it breaks the 200KB artifact size budget.
   Ordering rule: the forbidden-API scan runs BEFORE CSP injection, so the
   scan never sees (and never has to exempt) the origin literal we inject.
4. Parent page CSP (app-level) additionally set via Next.js headers, including `frame-ancestors 'self'`.
5. The parent never posts messages into the artifact iframe. One-way bridge only.

## 3. Forbidden-API policy (two independent enforcers)

Deny list checked by BOTH the Verifier (LLM, semantic: catches obfuscation like `window["fe"+"tch"]`) AND postprocess.py (deterministic string/AST scan: catches what the LLM misses):

fetch, XMLHttpRequest, WebSocket, EventSource, navigator.sendBeacon, importScripts, import( , eval, new Function, document.cookie, localStorage, sessionStorage, indexedDB, window.open, window.parent (except the sanctioned axiom postMessage lines), window.top, location.assign/replace/href writes, Notification, geolocation, getUserMedia, serviceWorker, SharedWorker, Worker (v1: no workers), any http:// or https:// literal, any protocol-relative // URL.

Post-processor verdict on a hit is reject (counts as a verifier fail for retry purposes), never auto-strip. Auto-stripping produces silently broken artifacts.

## 4. The delivery gate

`backend/services/delivery.py` exposes the only function that can emit `artifact_done`. Its signature requires a `PassedVerifierReport`, a class whose constructor is private to the verifier module and only instantiated on a pass verdict. Code review rule: any PR adding a second constructor or a second emitter is rejected regardless of justification. This makes "unverified artifact reaches client" a type error.

## 5. Prompt injection posture

- The Generator never receives raw user text. It receives the ArtifactPlan produced by the Planner. The Planner receives the query but outputs only the structured plan schema; free-text smuggling into the plan is bounded by field types and lengths.
- The Verifier runs with a fresh context containing only: plan, code, verifier prompt. It is instructed that the code is untrusted and that any instruction-like content inside code comments must be ignored and reported as a safety issue.
- Hostile suite (evals/hostile.yaml) includes: exfiltration requests, cookie access requests, instruction-injection inside the science question, instruction-injection via remix instruction, and oversized/degenerate inputs. All must be blocked by at least two layers.

## 6. Data and privacy

- Sessions are anonymous; no accounts, no emails, no names in v1. No PII columns in the schema; adding one requires updating this doc first.
- User queries and interaction events are stored for product function (tutor context, cache, evals). Interaction events aggregate-and-delete after 30 days.
- No user-specific data is ever embedded in artifact HTML (artifacts are shared via cache; see T5).
- API keys only in environment; never in frontend bundles; `/api` proxies all model calls.

## 7. Operational security

- Dependencies: lockfiles committed; automated vulnerability scan in CI; upgrades are dedicated PRs.
- Vendored libs: CHECKSUMS.txt verified in CI on every build.
- Rate limits and cost ceilings per API_SPEC.md and config.py.
- Incident switch: `ARTIFACTS_DISABLED=true` env flag forces text-only mode app-wide without redeploy.

## 8. Known accepted risks (v1)

- `script-src 'unsafe-inline'` is required for single-document artifacts. Accepted because the iframe origin is opaque and connect-src is 'none'; the blast radius of inline script is the artifact's own sandbox.
- Main-thread infinite loops in an artifact can freeze the iframe (not the app). Accepted for v1; user remedy is reset/close. Revisit worker-based execution only if this becomes a real-user complaint.
- Verifier is probabilistic. Mitigated by deterministic postprocess layer for safety checks and by the flag/evict loop for science checks; residual risk accepted and monitored via weekly hand audits.
