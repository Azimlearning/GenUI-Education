# Router Distillation (experiment track)

Train a small TensorFlow classifier that routes science questions by scoped
experiment type and subject: query -> { artifact_type, domain, complexity }.
The teacher is our production LLM Router (haiku + prompts/router.md); the
student is a tiny text model that runs in milliseconds on CPU.

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

## Status (2026-07-18)

**Not production-ready.** Trained on 1057 rows (846 train / 211 held-out):

| Metric | Target | Achieved |
|---|---|---|
| artifact_type accuracy | >= 90% | 67.3% |
| domain accuracy | >= 92% | 78.7% |
| complexity accuracy | (no target set) | 73.9% |
| text_only recall | >= 95% | 86.7% |

None of the targets are met. See "Known limitation" below before spending
more time tuning the model itself; the evidence points at data volume, not
architecture, as the bottleneck.

## Known limitation: data volume, not model capacity

Two model configurations were tried against the same 846-row training set:
the baseline (64-dim embedding, 128-unit dense, dropout 0.3) and a more
heavily regularized variant (32-dim embedding, L2 weight decay, dropout 0.5,
meant to fight the visible train/val gap: train accuracy reached 91%+ while
validation plateaued around 65-69%). The regularized variant scored WORSE on
held-out data (artifact_type 64.5% vs 65.9%, domain 74.4% vs 77.8%) and
converged more slowly to essentially the same ceiling. If overfitting were
the fixable cause, shrinking capacity should have closed the gap; it did
not. That rules out capacity as the lever to pull here.

A second piece of evidence: `generate_curriculum_dataset.py`'s own generation
step, which deliberately writes queries in a style intended to match a
specific `artifact_type`, only got the teacher to agree with that intended
style 75% of the time. A quarter of even the CONSTRUCTED examples are
genuinely ambiguous by the teacher's own judgment (e.g. "how do enzymes
work" is defensibly text_only or explorable_diagram). That puts a real,
non-architectural ceiling on what any classifier can learn from this data
without more examples to average the ambiguity out.

**Next step, if this track continues:** generate 2 to 3x more curriculum
data (`--per-style 6` to `8` instead of the current 3) before touching
hyperparameters again. Do not re-run the regularization experiment; it is
already answered.

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
│                                     (illustrative, drafted from general knowledge;
│                                     see ml/rag/ for grounding it in real syllabus text)
├── generate_dataset.py               generic query synth + teacher labels (v1)
├── generate_curriculum_dataset.py    topic- and style-diverse synth + teacher labels (kssm*)
├── prepare_dataset.py                cleaning: validate, normalize, dedupe, split 80/20
├── train_local.py                    TensorFlow training, local
├── train_colab.ipynb                 same model, Colab-ready
├── EXPERIMENT_SCHEMA.md              target schema for a future, richer per-query record
├── dataset/
│   ├── raw/                          stage-1 queries before labeling (queries_<tag>.txt)
│   ├── labeled/                      teacher-labeled rows (labeled_<tag>.jsonl)
│   └── clean/                        train.jsonl, test.jsonl, stats.json (train-ready)
└── out/                              trained artifacts (gitignored): .keras, saved_model/,
                                       .tflite, metrics.json, labels.json
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

# 1b. KSSM curriculum-scoped, style-diverse synthesis (recommended: this is
#     what fixed the v1 class imbalance, see "Known limitation" above)
..\..\backend\.venv\Scripts\python generate_curriculum_dataset.py --tag kssm1
#     --per-style N controls volume: 3 (default) gave 599 rows across 40
#     topics; use --topics-limit K for a cheap test run first.

# 2. clean + merge every dataset/labeled/*.jsonl + split
python prepare_dataset.py

# 3a. train on Colab: upload train_colab.ipynb + dataset/clean/train.jsonl
#     + dataset/clean/test.jsonl, then Run all
# 3b. or train locally (pip install -r requirements.txt first):
python train_local.py

# 4. artifacts land in ./out (keras, saved_model/, tflite, metrics.json)
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
