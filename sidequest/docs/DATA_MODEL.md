# DATA_MODEL.md — Axiom Postgres Schema

Managed by Alembic. This doc is the design intent; migrations are the source of truth. Update both together.

## Tables

### artifacts
The verified artifact cache and library.
```sql
CREATE TABLE artifacts (
  id              TEXT PRIMARY KEY,            -- art_<nanoid>
  cache_key       TEXT UNIQUE NOT NULL,        -- sha256(domain|type|concept)
  canonical_concept TEXT NOT NULL,
  domain          TEXT NOT NULL,               -- physics|chemistry|biology|earth_space|math_adjacent
  artifact_type   TEXT NOT NULL,               -- simulation|explorable_diagram|virtual_experiment|data_visualization
  title           TEXT NOT NULL,
  plan            JSONB NOT NULL,              -- ArtifactPlan
  html            TEXT NOT NULL,               -- post-processed, verified
  verifier_report JSONB NOT NULL,
  screenshot_path TEXT,                        -- Playwright capture at write time
  model_version   TEXT NOT NULL,
  prompt_version  TEXT NOT NULL,               -- generator prompt version header
  size_bytes      INT NOT NULL,
  serve_count     INT NOT NULL DEFAULT 0,
  rating_sum      INT NOT NULL DEFAULT 0,
  rating_count    INT NOT NULL DEFAULT 0,
  evicted         BOOLEAN NOT NULL DEFAULT FALSE,
  evicted_reason  TEXT,                        -- wrong_science|low_rating|model_bump|runtime_crash
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_artifacts_library ON artifacts(domain, evicted, created_at DESC);
CREATE INDEX idx_artifacts_concept ON artifacts(canonical_concept);
```
Notes: avg_rating computed as rating_sum/nullif(rating_count,0). Evicted rows are retained (audit trail, regression evals) but excluded from cache reads and library.

### sessions
```sql
CREATE TABLE sessions (
  id          TEXT PRIMARY KEY,               -- server-issued opaque
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_active TIMESTAMPTZ NOT NULL DEFAULT now(),
  gen_count_window INT NOT NULL DEFAULT 0,    -- rolling-hour generation counter
  gen_window_start TIMESTAMPTZ
);
```
Anonymous by design in v1. No PII columns exist; do not add any without a SECURITY.md update.

### messages
```sql
CREATE TABLE messages (
  id          BIGSERIAL PRIMARY KEY,
  session_id  TEXT NOT NULL REFERENCES sessions(id),
  role        TEXT NOT NULL,                  -- user|assistant|tutor
  content     TEXT NOT NULL,
  artifact_id TEXT REFERENCES artifacts(id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_session ON messages(session_id, id);
```

### interaction_events
```sql
CREATE TABLE interaction_events (
  id          BIGSERIAL PRIMARY KEY,
  session_id  TEXT NOT NULL REFERENCES sessions(id),
  artifact_id TEXT NOT NULL REFERENCES artifacts(id),
  control     TEXT NOT NULL,
  value       TEXT NOT NULL,                  -- stringified; typed client-side only
  ts          TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_events_session_artifact ON interaction_events(session_id, artifact_id, ts);
```
Retention: 30 days, then aggregate-and-delete (keep per-artifact control usage counts in a summary table if needed later).

### feedback
```sql
CREATE TABLE feedback (
  id          BIGSERIAL PRIMARY KEY,
  artifact_id TEXT NOT NULL REFERENCES artifacts(id),
  session_id  TEXT NOT NULL REFERENCES sessions(id),
  rating      SMALLINT NOT NULL,              -- 1 | -1
  flag_reason TEXT,                           -- wrong_science|broken|confusing
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (artifact_id, session_id)
);
```
Triggered logic (application layer, not DB triggers): on wrong_science flag, set artifacts.evicted immediately; on rating insert/update, refresh rating_sum/rating_count; eviction check avg < 2.5 with rating_count >= 3.

### traces
```sql
CREATE TABLE traces (
  id             BIGSERIAL PRIMARY KEY,
  run_id         TEXT NOT NULL,               -- one per /ask or /modify request
  session_id     TEXT NOT NULL,
  node           TEXT NOT NULL,
  model          TEXT,
  prompt_version TEXT,
  tokens_in      INT, tokens_out INT,
  cost_usd       NUMERIC(8,5),
  latency_ms     INT,
  verdict        TEXT,                        -- verifier only: pass|fail
  retry_index    SMALLINT NOT NULL DEFAULT 0,
  error          TEXT,
  details        JSONB,                       -- structured telemetry; never raw queries
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_traces_run ON traces(run_id);
CREATE INDEX idx_traces_cost ON traces(created_at, cost_usd);
```

## Pydantic schema anchors (backend/schemas)

```python
class Intent(BaseModel):
    artifact_type: Literal["simulation","explorable_diagram",
        "virtual_experiment","data_visualization","text_only"]
    domain: Literal["physics","chemistry","biology","earth_space","math_adjacent"]
    complexity: Literal[1,2,3]
    canonical_concept: str          # snake_case, normalized

class ArtifactPlan(BaseModel):
    title: str
    learning_objective: str
    variables: list[Variable]       # name, unit, min, max, default (1..3 items)
    governing_model: str            # explicit equations/mechanism text
    expected_behaviors: list[str]   # qualitative assertions the Verifier checks
    layout_notes: str
    library: Literal["p5","matter","three","chart","d3","none"]

class VerifierIssue(BaseModel):
    severity: Literal["blocker","major","minor"]
    category: Literal["science","behavior","interactivity","safety","pedagogy"]
    description: str
    fix_hint: str

class VerifierReport(BaseModel):
    verdict: Literal["pass","fail"]
    issues: list[VerifierIssue]
    spot_checks: list[SpotCheck]    # input values, expected, code-derived
```

## Migration policy

One migration per PR maximum. Never edit an applied migration. Destructive changes (drops, type narrowing) require a two-step deploy (add new, backfill, switch, drop later).
