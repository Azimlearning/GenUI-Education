# API_SPEC.md — Axiom API, SSE Protocol, Bridge Contract

All endpoints prefixed `/api`. JSON bodies validated with pydantic; responses typed. Errors follow `{error: {code, message, retryable}}`.

## 1. Endpoints

### POST /api/ask
Primary pipeline entry. Streams SSE.
```
Request:  { session_id: string, message: string }
Response: text/event-stream (protocol below)
Errors:   429 rate_limited (retryable), 503 llm_unavailable (retryable)
```

### POST /api/artifact/{artifact_id}/modify
Remix cycle. Streams SSE (same protocol; meta.cache is always "miss").
```
Request:  { session_id: string, instruction: string }   # "add air resistance"
```

### POST /api/artifact/{artifact_id}/event
Interaction events from the bridge. Fire-and-forget from client perspective.
```
Request:  { session_id, control: string, value: string|number|boolean, ts: iso8601 }
Response: 204
```
Server batches per session (flush every 5s or 20 events) before Tutor consideration.

### POST /api/artifact/{artifact_id}/feedback
```
Request:  { session_id, rating: 1|-1, flag_reason?: "wrong_science"|"broken"|"confusing" }
Response: 204. wrong_science triggers immediate cache eviction.
```

### GET /api/library?domain=&q=&page=
```
Response: { items: [{artifact_id, title, domain, artifact_type,
            canonical_concept, screenshot_url, serve_count, avg_rating}], next_page }
```

### GET /api/library/{artifact_id}
```
Response: { artifact_id, html, plan_summary, created_at }
```

### GET /vendor/{file}
Static pinned libraries. Immutable cache headers.

## 2. SSE protocol

Content type `text/event-stream`. Every event carries `id:` (monotonic per stream) for future resume support. Client validates each payload against zod schemas in `frontend/types/events.ts`, which must stay mirrored with `backend/schemas/events.py`.

```
event: meta
data: {"intent": {"artifact_type": "simulation", "domain": "physics",
       "complexity": 2}, "canonical_concept": "projectile_motion",
       "cache": "miss"}

event: text_delta
data: {"chunk": "When you launch a projectile..."}      # repeats

event: text_done
data: {}

event: artifact_status
data: {"stage": "planning"}      # planning | generating | verifying
                                 # | revising | postprocessing

event: artifact_delta            # optional; only when client opts in
data: {"chunk": "<canvas id=..."}

event: artifact_done
data: {"artifact_id": "art_9f3c", "title": "Projectile Motion Lab",
       "html": "<!doctype html>..."}

event: artifact_failed
data: {"reason": "verification_failed", "detail_user": "I couldn't build a
       stable simulation for this one.", "retryable": true}

event: tutor_msg
data: {"text": "You pushed the angle past 45 degrees. What happened to the range?"}

event: done
data: {"usage": {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0},
      "timings_ms": {"first_token": 0, "artifact_total": 0}}
```

Ordering guarantees:
1. `meta` is always first, `done` always last.
2. `text_delta` events may interleave with `artifact_status` events (parallel branches).
3. Exactly one of `artifact_done` / `artifact_failed` per request when meta.intent is not text_only; neither when it is.
4. `tutor_msg` never appears before `artifact_done`.

## 3. Bridge contract (iframe ⇄ parent)

Inbound only (iframe to parent). Parent never posts into the iframe.

```ts
// zod, frontend/lib/bridge.ts
const BridgeMessage = z.discriminatedUnion("type", [
  z.object({ type: z.literal("axiom_ready") }),
  z.object({ type: z.literal("axiom_event"),
             control: z.string().max(64),
             value: z.union([z.string().max(256), z.number(), z.boolean()]) }),
  z.object({ type: z.literal("axiom_error"), message: z.string().max(512) }),
]);
```

Parent listener rules:
- Accept only messages whose `source` is the mounted artifact iframe's contentWindow.
- Validate with BridgeMessage; silently drop failures (log count).
- Rate-limit forwarding to 10 events/second per artifact; coalesce slider drags to trailing value.
- Treat all bridge values as untrusted display data: never interpolate into HTML, never eval, never use as URLs.

## 4. Rate limiting

- Generation endpoints (ask with artifact intent, modify): 10/hour/session, 429 with Retry-After.
- Cache hits, library reads, events, feedback: not generation-limited; generic 60 req/min/IP.
- Session id is a server-issued opaque cookie value; do not trust client-fabricated ids for limits (key limits on cookie + IP pair).

## 5. Versioning

Prefix breaking changes as /api/v2 only if external consumers appear. For v1, frontend and backend deploy together; schema mirror files are the compatibility contract and CI fails if they drift (schema snapshot test).
