# evals

Data and harness for the golden and hostile suites. Strategy and the meaning of
each metric live in `docs/EVALS.md`; this directory holds the executable side.

## Status

Phase 0 ships the data contracts only:

- `golden.yaml`: the 12 golden queries, their expected routes, and assertions.
- `hostile.yaml`: the 5 hostile inputs and the layers that must block each one.

The runner arrives with the pipeline it exercises:

| File | Arrives in | Purpose |
|---|---|---|
| `run.py` | Phase 1 | Drive the full pipeline, write metrics to `history.jsonl` |
| `render_check.py` | Phase 1 | Playwright: axiom_ready, control wiring, forbidden-API scan |
| `fixtures/` | Phase 1 | Recorded LLM request/response pairs so CI replays free and deterministic |
| `audits/` | Phase 2 | Weekly hand-audit logs (EVALS.md section 8) |

`make evals` and `make evals-smoke` fail loudly until `run.py` exists, rather
than reporting a false green.

## Cost

Live runs spend real tokens: roughly $1 to $3 for the smoke subset and $5 to $15
for the full set. Run the smoke subset while tuning prompts and the full set
before a phase completes. Confirm before running either.
