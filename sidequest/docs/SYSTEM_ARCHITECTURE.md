# SYSTEM_ARCHITECTURE.md — Axiom

Authoritative architecture reference. If code and this doc disagree, fix one of them in the same PR.

## 1. Component overview

```
┌────────────────────────────── Browser ──────────────────────────────┐
│  Next.js app                                                        │
│  ┌───────────┐  ┌──────────────────────────────┐  ┌─────────────┐  │
│  │ Chat UI   │  │ Artifact Card                │  │ /library    │  │
│  │ (SSE      │  │ ┌──────────────────────────┐ │  │ (cache      │  │
│  │ consumer) │  │ │ iframe sandbox=          │ │  │ browser)    │  │
│  │           │  │ │ "allow-scripts" srcdoc   │ │  └─────────────┘  │
│  └───────────┘  │ └──────────▲───────────────┘ │                   │
│                 │   postMessage bridge          │                   │
│                 └──────────────────────────────┘                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS (SSE + JSON)
┌──────────────────────────────▼──────────────────────────────────────┐
│  FastAPI backend                                                    │
│  ┌──────────────┐   ┌───────────────────────────────────────────┐  │
│  │ API layer    │──▶│ LangGraph pipeline                        │  │
│  │ (SSE emitter)│   │ Router → [Explainer ∥ artifact branch]    │  │
│  └──────┬───────┘   │ artifact: Cache → Planner → Generator     │  │
│         │           │           → Verifier ⇄ retry → Postproc   │  │
│         │           └───────────────┬───────────────────────────┘  │
│         │                           │ Claude API                    │
│  ┌──────▼──────────────────────┐    │                               │
│  │ Postgres                    │    │                               │
│  │ artifacts, sessions,        │    │                               │
│  │ messages, events, feedback, │    │                               │
│  │ traces                      │    │                               │
│  └─────────────────────────────┘    │                               │
└─────────────────────────────────────┴───────────────────────────────┘
```

## 2. The two-branch request flow

Every `/api/ask` request forks into two concurrent branches after the Router:

- **Text branch (fast path):** Explainer streams `text_delta` events immediately. Never waits on the artifact branch. Target: first token under 2 seconds.
- **Artifact branch (slow path):** Cache lookup, then Planner → Generator → Verifier loop → Post-processor. Emits `artifact_status` stage events throughout, then `artifact_done` or `artifact_failed`.

Both branches multiplex onto one SSE response. The client demuxes by event type.

## 3. Sequence: cache miss with one verifier retry

```
Client          API           Router   Explainer  Cache  Planner  Generator  Verifier  Postproc
  │──ask───────▶│              │          │         │       │         │          │        │
  │             │──classify───▶│          │         │       │         │          │        │
  │◀─meta───────│◀─intent──────│          │         │       │         │          │        │
  │             │──────────────┼─stream──▶│         │       │         │          │        │
  │◀─text_delta─│◀─────────────┼──────────│         │       │         │          │        │
  │             │──lookup──────┼──────────┼────────▶│ miss  │         │          │        │
  │◀─status:planning───────────┼──────────┼─────────┼──────▶│         │          │        │
  │◀─status:generating─────────┼──────────┼─────────┼───────┼────────▶│          │        │
  │◀─status:verifying──────────┼──────────┼─────────┼───────┼─────────┼─────────▶│ fail   │
  │◀─status:revising───────────┼──────────┼─────────┼───────┼────────▶│ (issues) │        │
  │◀─status:verifying──────────┼──────────┼─────────┼───────┼─────────┼─────────▶│ pass   │
  │◀─status:postprocessing─────┼──────────┼─────────┼───────┼─────────┼──────────┼───────▶│
  │◀─artifact_done──────────── │  (html)  │         │ write │         │          │        │
  │◀─done───────│              │          │         │       │         │          │        │
```

## 4. LangGraph state

```python
class PipelineState(TypedDict):
    session_id: str
    query: str
    intent: Intent | None            # Router output (pydantic)
    canonical_concept: str | None
    cache_key: str | None
    explanation_done: bool
    artifact_plan: ArtifactPlan | None
    artifact_code: str | None
    verification_report: VerifierReport | None
    retry_count: int                 # hard cap 2
    prior_artifact_html: str | None  # set only in modification cycles
    final_artifact_id: str | None
    failure_reason: str | None
```

Conditional edges:
- Router → END(text branch only) when `intent.artifact_type == text_only`
- Cache → delivery when hit, → Planner when miss
- Verifier → Postproc on pass; → Generator when fail and retry_count < 2; → degrade otherwise

## 5. Node model assignments

| Node | Model tier | Rationale |
|---|---|---|
| Router | fast | classification, strict JSON, latency-critical |
| Explainer | fast | conversational text, latency-critical |
| Planner | strongest | equations and behavior contract must be right |
| Generator | strongest, high max tokens | the Tier 3 core |
| Verifier | strongest | recomputes physics; independence from Generator context is mandatory |
| Tutor | fast | conversational, frequent, cheap |

## 6. Artifact runtime and bridge

- Mount: `<iframe sandbox="allow-scripts" srcdoc={html} title={artifactTitle}>`.
- The parent page and iframe are cross-origin by construction (srcdoc + no allow-same-origin), so the generated code cannot touch parent DOM, cookies, or storage.
- **Inbound (iframe → parent):** `window.parent.postMessage({type, ...}, "*")` with types `axiom_ready`, `axiom_event {control, value}`, `axiom_error {message}`. Parent validates with zod, drops anything else, forwards events to `POST /api/artifact/{id}/event`.
- **Outbound (parent → iframe):** nothing. The parent never posts into the iframe. Remix and reset are implemented by remounting with new srcdoc.
- Watchdog: no `axiom_ready` within 5s, or any `axiom_error`, swaps card to degraded state.
- Only the active (viewport-visible, most recent) artifact iframe stays mounted; history artifacts render as static screenshots (Playwright capture stored at cache-write time) until clicked.

## 7. Delivery gate (structural safety)

`artifact_done` events are constructed exclusively by `deliver_verified_artifact(report: PassedVerifierReport, ...)`. `PassedVerifierReport` is a distinct type only instantiable by the verifier module on a pass verdict. There is no other constructor and no code path from Generator output to the SSE emitter. Bypassing verification must be a type error, not a code-review catch.

## 8. Caching architecture

- Key: `sha256(domain + "|" + artifact_type + "|" + canonical_concept)`; canonical_concept is produced by the Router with a normalization prompt rule (snake_case, singular, qualifier-ordered).
- Write: after verifier pass + post-process, alongside plan, report, model_version, and a Playwright screenshot.
- Read: cache node queries by key where not evicted; serve_count incremented.
- Eviction: any `wrong_science` flag, or avg_rating < 2.5 with n ≥ 3 ratings, or model_version bump (lazy: served stale until re-requested, then regenerated).
- Near-duplicate handling v1 is exact-key only. Semantic dedup (embedding similarity over canonical concepts) is a later optimization; do not build it in v1.

## 9. Trace and observability

Every node call writes a trace row: run_id, node, model, prompt_version, input_hash, output_hash, tokens_in/out, cost, latency_ms, verdict (verifier only). The cost dashboard and eval metrics both read from traces. During prompt tuning this table is the primary debugging surface.

## 10. Failure taxonomy

| Failure | Detection | User experience |
|---|---|---|
| Generator invalid JSON/HTML | pydantic/parse | one silent retry, then counts as verifier fail |
| Verifier fail x3 | retry cap | text + honest degrade card + retry button |
| Artifact runtime crash | axiom_error / watchdog | degrade card + retry; auto-flag artifact in cache |
| Artifact branch timeout 30s | asyncio timeout | degrade card; text unaffected |
| SSE disconnect | client reconnect | idempotent replay from last event id (v1: simple restart of request) |
| Claude API outage | circuit breaker | text-only mode banner |
