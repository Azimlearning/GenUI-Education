# evals

Data and harness for the golden and hostile suites. Strategy and the meaning of
each metric live in `docs/EVALS.md`; this directory holds the executable side.

## Status

- `golden.yaml`: the 12 golden queries, their expected routes, and assertions.
- `hostile.yaml`: the 5 hostile inputs and the layers that must block each one.
- `run.py` (Phase 1): drives a running backend through each golden query,
  asserts routing and artifact delivery, appends metrics to `history.jsonl`.
  Flags: `--smoke`, `--only G2`, `--render`, `--base-url`.
- `render_check.py` (Phase 1): Playwright checks on one artifact, mounted
  exactly as production mounts it (sandboxed srcdoc iframe, /vendor served
  same-origin): axiom_ready within 5s, forbidden-API scan on model-authored
  content, control wiring via screenshot diff, no page errors.

Setup: `pip install -r requirements.txt && playwright install chromium`.

Still to come:

| File | Arrives in | Purpose |
|---|---|---|
| `fixtures/` | Phase 2 | Recorded LLM request/response pairs so CI replays free and deterministic |
| `audits/` | Phase 2 | Weekly hand-audit logs (EVALS.md section 8) |
| memory/reset checks | Phase 2 | render_check items 5 and 6 from EVALS.md section 4 |

## Cost

Live runs spend real tokens: roughly $1 to $3 for the smoke subset and $5 to $15
for the full set. Run the smoke subset while tuning prompts and the full set
before a phase completes. Confirm before running either.
