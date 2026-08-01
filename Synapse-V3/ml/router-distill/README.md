# Router Distillation (experiment track)

Train a small TensorFlow classifier that routes science questions by scoped
experiment type and subject: query -> { artifact_type, domain, complexity }.
The teacher is our production LLM Router (haiku + prompts/router.md); the
student is a tiny text model that runs in milliseconds on CPU.

**For what happens once the full KSSM dataset is collected** (ingestion at
scale, topic grounding, regeneration, production integration), see
[`../IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md).

## Why

| | LLM Router (today) | Distilled student |
|---|---|---|
| Latency | ~1.5 s | ~5 ms |
| Cost per query | ~$0.001 | 0 |
| Offline / rate-limit proof | no | yes |

Routing latency sits directly in front of the first text token (Phase 3 DoD
wants < 2 s), so this is the cheapest remaining latency lever.

Scope honesty: `canonical_concept` (the cache key label) is open-vocabulary
generation, not classification. The student does NOT produce it. Integration
plan keeps the LLM in the loop for concept labeling, or defers it to the
artifact branch where its latency does not block text.

This track does not replace Phase 4 (cache + library); it runs alongside it.

## Status (2026-07-18, round 3: independent cross-check found + fixed 4 more topic errors)

An independent topic-grounding report (`TOPIC_GROUNDING_REPORT.md`, produced
separately from this session's own extraction, found unstaged in the repo
partway through round 2's work) largely CONFIRMED round 2's major
corrections but also caught what round 2 missed: 2 entire Biology Form 4
chapters (Support and Movement; Sexual Reproduction/Development/Growth) and
a genuine placement conflict on Chemistry's "Manufactured Substances in
Industry" (round 2 had put it in Form 5; two independent sources, including
round 2's own discarded direct-text evidence, agree it's Form 4). Fixed in
`kssm_topics.py` v3 (50 -> 53 topics), plus a newly-recognized distinct
Form 5 "Polymer" chapter.

A small, targeted generation round (`--tag kssm3 --topics-contains
"support_and_movement,reproduction_development_growth,manufactured_substances_in_industry,polymer"`,
120 rows, ~$0.20-0.40) closed the gap without a full 53-topic re-generation.
Final dataset: 2693 rows (2154 train / 538 held-out). Metrics moved little
(artifact_type 69.3%, domain 86.4%, complexity 76.8%, text_only recall
80.3% — some within noise of round 2's numbers, a couple slightly down),
consistent with round 2's own plateau finding rather than contradicting it.
**This round's value was correctness, not a metrics bump**: earlier rounds
trained on data where two real curriculum chapters were entirely absent and
one topic was tagged to the wrong form. A model trained on curriculum-
accurate data is more trustworthy than one trained on slightly more data
that misrepresents the curriculum, even at a similar accuracy score.

kssm1's `curriculum_topic` tags are now stale against v3 in TWO ways (v2's
corrections, then v3's); kssm2 additionally has
`chemistry_form5_manufactured_substances_in_industry` rows that are stale
against v3's `chemistry_form4_...` placement. None of this corrupts the
core classifier training (artifact_type/domain/complexity labels are
unaffected), only the `curriculum_topic` metadata field on older rows.

## Status (2026-07-18, round 2: grounded topics + 2x data + learning-curve study)

**Still not production-ready, but the picture is clearer and improved.**
Full dataset now 2573 rows (2058 train / 514 held-out), combining v1
(generic), kssm1 (curriculum, uncorrected topics), and kssm2 (curriculum,
corrected topics + retrieval-anchored generation, see
`../IMPLEMENTATION_PLAN.md` Phases 2-3):

| Metric | Target | Round 1 (1057 rows) | Round 2 (2573 rows) |
|---|---|---|---|
| artifact_type accuracy | >= 90% | 67.3% | 70.4% |
| domain accuracy | >= 92% | 78.7% | **88.1%** |
| complexity accuracy | (no target set) | 73.9% | 78.6% |
| text_only recall | >= 95% | 86.7% | 84.8% |

domain accuracy is now within 4 points of target and still clearly rising
with data (see the learning curve below). artifact_type is not: it improved
but the curve is plateauing, a materially different and more honest picture
than round 1's blanket "gather more data" recommendation.

## Learning-curve study (`learning_curve.py`)

Trained on 25%, 50%, 75%, 100% of the training set, same architecture, no
hyperparameter changes (`out/learning_curve.json`):

| Train n | artifact_type | domain | complexity |
|---|---|---|---|
| 514 (25%) | 63.4% | 71.4% | 74.9% |
| 1029 (50%) | 70.0% | 80.4% | 75.3% |
| 1543 (75%) | 68.7% | 84.2% | 74.3% |
| 2058 (100%) | 70.4% | 85.6% | 77.4% |

**domain**: clean, consistent rise across every step (+14.2 points end to
end). Unambiguously still data-bound; another round of data should keep
closing the gap to 92%.

**artifact_type**: a real jump from 25% to 50% (+6.6 points), then
flat/noisy from 50% to 100% (70.0 -> 68.7 -> 70.4). This is NOT the same
shape as domain's curve. Two live explanations, not mutually exclusive: (1)
the 75% teacher-self-disagreement rate on deliberately-styled queries (see
round-1 finding below) caps how much any volume of this kind of data can
teach the model, since a quarter of the "ground truth" is itself
inconsistent; (2) `GlobalAveragePooling1D` bag-of-words averaging may
genuinely not carry enough of the phrasing signal ("show me" vs "explain")
that separates these five classes, independent of data volume. Round 1's
"just add more data" recommendation undersold this; it is now a real,
evidence-backed open question rather than an assumption.

**Next step, if this track continues:** for domain, generate another round
of data, same method, and expect continued improvement. For artifact_type,
do not blindly repeat that; either (a) try a small architecture change (a
pretrained embedding, or an n-gram/positional feature that preserves some
word order) on the EXISTING 2058 rows first, since more data alone has
stopped moving this specific metric, or (b) accept the ceiling and lean on
Phase 4's confidence-gated fallback (low-confidence artifact_type
predictions fall back to the LLM router; that path was always the plan for
exactly this situation, not a failure mode).

## Round 1 finding: data volume was ruled out as a capacity/overfitting problem

Two model configurations were tried against the round-1 846-row training
set: the baseline (64-dim embedding, 128-unit dense, dropout 0.3) and a more
heavily regularized variant (32-dim embedding, L2 weight decay, dropout 0.5,
meant to fight the visible train/val gap: train accuracy reached 91%+ while
validation plateaued around 65-69%). The regularized variant scored WORSE on
held-out data (artifact_type 64.5% vs 65.9%, domain 74.4% vs 77.8%) and
converged more slowly to essentially the same ceiling. If overfitting were
the fixable cause, shrinking capacity should have closed the gap; it did
not. That ruled out capacity as the lever to pull, and motivated round 2's
data-volume increase, which is why domain's clean improvement (and
artifact_type's more complicated one) is meaningful evidence rather than
noise.

`generate_curriculum_dataset.py`'s own generation step, which deliberately
writes queries in a style intended to match a specific `artifact_type`, only
got the teacher to agree with that intended style 75% (round 1) / 56% (round
2, after adding retrieval-anchored, more textbook-realistic phrasing) of the
time. Realistic phrasing surfaces MORE genuine ambiguity, not less; this is
expected and is itself evidence the label noise explanation for
artifact_type's plateau is real, not a generation artifact.

## Not in scope (and why)

Training a model to GENERATE artifacts is explicitly out of scope for now:
useful code generation needs a large base model and thousands of verified
training examples; we have a handful. The Phase 4 cache is the long game
here: every verified artifact it accumulates is future fine-tuning data.
Revisit when the library holds hundreds of rated artifacts.

## Layout

```
ml/router-distill/
├── kssm_topics.py                   KSSM Form 4/5 topic taxonomy, Bio/Chem/Phy
│                                     (v2: grounded in real textbook chapters via
│                                     ml/rag/extract_toc.py; see the file's own
│                                     docstring for the v1 -> v2 correction log)
├── generate_dataset.py               generic query synth + teacher labels (v1)
├── generate_curriculum_dataset.py    topic- and style-diverse synth + teacher labels
│                                      (kssm1: uncorrected topics; kssm2: corrected
│                                      topics + retrieval-anchored generation)
├── prepare_dataset.py                cleaning: validate, normalize, dedupe, split 80/20
├── train_local.py                    TensorFlow training, local
├── learning_curve.py                 trains at 25/50/75/100% of data, same architecture,
│                                      to test whether more data is still the right lever
├── train_colab.ipynb                 same model, Colab-ready
├── EXPERIMENT_SCHEMA.md              target schema for a future, richer per-query record
├── TOPIC_GROUNDING_REPORT.md         independent topic cross-check that caught v3's corrections
│                                      (contents-page reading, separate method from extract_toc.py)
├── dataset/
│   ├── raw/                          stage-1 queries before labeling (queries_<tag>.txt)
│   ├── labeled/                      teacher-labeled rows (labeled_<tag>.jsonl)
│   └── clean/                        train.jsonl, test.jsonl, stats.json (train-ready)
└── out/                              trained artifacts (gitignored): .keras, saved_model/,
                                       .tflite, metrics.json, labels.json, learning_curve.json
```

Rows are `{query, artifact_type, domain, complexity}`, with curriculum rows
additionally carrying `curriculum_topic` / `curriculum_subject` /
`curriculum_form` / `intended_style` (the KSSM tag rides alongside the
generic routing labels, per the decision to keep them compatible with the
production Router schema in `backend/schemas/intent.py`, not replace it).
The teacher is always the real, unmodified production Router prompt, so the
student distills the deployed decision boundary, including its ambiguity.
Multiple labeled files (tags) accumulate; `prepare_dataset.py` merges all of
`dataset/labeled/*.jsonl`, so grow the dataset by generating another tag.

## Workflow

```
# 1a. generic query synthesis (cheap, ~$0.001/row)
..\..\backend\.venv\Scripts\python generate_dataset.py --n 500 --tag v1

# 1b. KSSM curriculum-scoped, style-diverse, retrieval-anchored synthesis
#     (recommended: this is what fixed v1's class imbalance and, once
#     kssm_topics.py is grounded, produces textbook-register queries).
#     Requires ml/rag/index/ to exist (ingest.py + embed.py run first) for
#     retrieval-anchoring; falls back to topic-only with --no-grounding.
..\..\backend\.venv\Scripts\python generate_curriculum_dataset.py --tag kssm2 --per-style 6
#     --per-style N controls volume per (topic, style) pair; --topics-limit K
#     for a cheap test run first. See kssm_topics.py's docstring before
#     trusting its topic-to-form placement for a NEW subject/form combo not
#     already grounded there.

# 2. clean + merge every dataset/labeled/*.jsonl + split
python prepare_dataset.py

# 3a. train on Colab: upload train_colab.ipynb + dataset/clean/train.jsonl
#     + dataset/clean/test.jsonl, then Run all
# 3b. or train locally (pip install -r requirements.txt first):
python train_local.py

# 3c. before concluding "need more data" again: check whether the curve is
#     actually still rising (see "Status" above; it was NOT uniform last time)
python learning_curve.py

# 4. artifacts land in ./out (keras, saved_model/, tflite, metrics.json,
#    learning_curve.json)
```

There is no Colab MCP in this environment; the Kaggle MCP can run the same
notebook on a free GPU if preferred (a GPU is overkill for this model; Colab
CPU or local CPU trains it in under a minute).

## Success criteria

- artifact_type accuracy vs teacher >= 90% on held-out
- domain accuracy >= 92%
- text_only recall >= 95% (never route junk to the artifact branch)
- model artifact < 5 MB, inference < 10 ms CPU

## Integration sketch (only after criteria met)

`ROUTER_MODE=local` in config: backend loads the exported model, classifies
locally, emits `meta` immediately, and fires the LLM once per artifact-bound
query for `canonical_concept` inside the artifact branch (off the text path).
Falls back to the full LLM router on low classifier confidence (< 0.7) or any
load error. The golden set (routing expectations in evals/golden.yaml) is the
regression gate before flipping the flag.
