# ML Track Implementation Plan — Router Distillation + Curriculum RAG

Companion to `ml/router-distill/README.md` and `ml/rag/README.md`. Those
documents explain what exists and why; this document is what happens next,
once the full curriculum dataset is collected. Phased like `docs/PLANNING.md`
so each phase has a checklist and an explicit Definition of Done (DoD) — no
phase starts until the previous one's DoD is met, same rule as the main app.

This plan does not replace or block Axiom's own Phase 4 (Cache and Library).
It is a separate track; the two can run in parallel.

## Trigger and current state

Activates once the full dataset is collected. "Full" means real source
material for all 6 subject/form combinations:

| Subject | Form 4 | Form 5 |
|---|---|---|
| Biology | textbook + experiments (have) | textbook (have), experiments (none yet) |
| Chemistry | textbook + experiments (have) | not started |
| Physics | not started | not started |

Current state as of 2026-07-18, verified, not assumed:

- `Dataset/` (repo root, gitignored, ~381MB): `BIOLOGY-...zip` (Biology Form
  4 + Form 5 textbooks, 2 real experiment PDFs: amylase activity, yeast
  fermentation), `CHEM-...zip` (Chemistry Form 4: 4-part Malay textbook + 1
  English textbook + 2 experiment/activity books).
- `ml/rag/sources/biology/form4/`: the 2 biology experiment PDFs, extracted
  and proof-of-concept tested (clean extraction, correct retrieval). Their
  chapter numbers (5.1, 7.3) were not cross-checked against an official Form
  4 table of contents — verify in Phase 2 below, they could belong in a
  different form.
- `ml/router-distill/kssm_topics.py`: 40 topics, hand-drafted from general
  knowledge, explicitly marked as needing validation against real source
  material (this plan is that validation).
- `ml/router-distill/` trained model: 1057 rows, held-out artifact_type
  accuracy 67.3% against a 90% target. Diagnosed as data-volume-bound, not
  architecture-bound (see README "Known limitation" before re-reading this
  as a tuning problem).

Phases 1 to 3 can run per-subject as material arrives; nothing requires all
6 combinations to be ready simultaneously except the final consolidated
retrain in Phase 3.

---

## Phase 1 — Full corpus ingestion

**Goal:** every supplied source file is chunked, embedded, and retrievable.

- [ ] Extract all PDFs from `Dataset/*.zip` into
      `ml/rag/sources/<subject>/form<N>/`, preserving original filenames
      (the filename is part of the citation).
- [ ] Run `ingest.py` at full scale. Textbooks are 40 to 100MB single PDFs,
      two orders of magnitude bigger than the proof-of-concept files;
      extraction time and memory are unverified at this scale, budget time
      for a first real run and watch for pypdf failures on scanned or
      image-heavy pages (silent empty-text extraction is the failure mode
      to watch for, not a crash).
- [ ] Spot-check extraction quality: for each source file, manually read 3
      random chunks. Acceptable: readable text, minor encoding artifacts
      (the `°C` -> `�C` issue already seen is cosmetic and acceptable).
      Not acceptable: garbled text, missing whole sections, OCR gibberish.
      Log failures per file; a badly-scanned PDF may need a different
      extraction path (OCR) not built here.
- [ ] Run `embed.py`. At an estimated several thousand passages from full
      textbooks, confirm the TF-IDF matrix build stays fast (seconds, not
      minutes) and `index/vectors.npz` stays a reasonable size (low tens of
      MB). If it does not, that is the signal to stop deferring a real
      embedding backend (see "Deferred: real embeddings" below).
- [ ] Write one retrieval smoke query per subject/form combo (e.g. "rate of
      reaction factors" for chemistry_form5) and confirm the top result is
      genuinely relevant, not just lexically overlapping.

**DoD:** every source file under `Dataset/` is ingested, embedded, and
returns relevant results for a hand-written smoke query in its subject/form.

## Phase 2 — Topic grounding

**Goal:** `kssm_topics.py` reflects real curriculum content, not general
knowledge.

- [ ] For each textbook, extract its table of contents (chapter/section
      headings). If the PDF has a navigable outline, `pypdf`'s
      `reader.outline` gives this directly; otherwise pattern-match heading-
      shaped lines (numbered like `5.1`, `Bab 7`, `Chapter 3`) in the first
      few ingested chunks per source file.
- [ ] Diff the extracted headings against the corresponding subject/form
      section of `kssm_topics.py`. Produce a plain report: topics present in
      the real TOC but missing from the hand-drafted list, topics in the
      hand-drafted list with no real-TOC match, and mismatched labels/order.
- [ ] **Human review required before merging.** This file feeds every
      downstream generation step; do not auto-apply the diff. Present it,
      get explicit correction or approval, then update `kssm_topics.py` with
      a comment citing the source file the correction came from.
- [ ] Re-verify the 2 biology experiment PDFs' chapter numbers (5.1, 7.3)
      against the real Form 4 and Form 5 tables of contents and correct
      their `curriculum_form` tag in `ml/rag/sources/` if they turn out to
      belong to a different form than currently placed.
- [ ] Chemistry and Biology only have Form 4 (Chemistry) or partial (Biology
      Form 5 experiments missing) source material at plan-trigger time,
      per the table above. Ground what exists; note what's still missing
      rather than leaving a silent gap.

**DoD:** every topic in `kssm_topics.py` traces to a real heading in a
supplied source file, with corrections reviewed and approved, not
auto-merged.

## Phase 3 — Grounded dataset regeneration and retraining

**Goal:** a router-distill dataset written in real curriculum register,
sized enough to test whether Phase 1 (README) findings hold ("data volume
is the bottleneck") or whether an architecture change is also needed.

- [ ] Re-run `generate_curriculum_dataset.py` against the corrected topic
      list from Phase 2.
- [ ] Optional but recommended: before generating each topic's queries,
      retrieve 1 to 2 real passages for that `curriculum_topic` via
      `ml/rag/retrieve.py` and include them in the generation prompt as a
      vocabulary/register anchor, so generated queries sound like they came
      from the actual textbook, not generic international-English science
      phrasing. This is new work, not yet built; keep it a small, isolated
      change so it is easy to A/B against the ungrounded version.
- [ ] Increase volume: `--per-style 6` to `8` (up from the current 3),
      per the README's explicit recommendation. Estimate cost before
      running: at v1 rates (~$0.001 to 0.002/row all-in on the fast model),
      40 topics x 5 styles x 8 = 1600 rows is roughly $2 to $4. Confirm
      before spending if the topic count grows materially past 40 once
      Physics and Chemistry Form 5 are added.
- [ ] Run `prepare_dataset.py` to merge every `dataset/labeled/*.jsonl` file
      (old and new tags both count) and re-split.
- [ ] **Do a learning-curve check before declaring victory or defeat.**
      Train on 25%, 50%, 75%, and 100% of the merged training set (same
      architecture, no hyperparameter changes) and plot held-out
      artifact_type accuracy against training-set size. Rising curve at
      100% => more data still helps, gather another round. Flattening curve
      well below the 90% target => the architecture itself is now the
      bottleneck (bag-of-words averaging losing genuinely order-dependent
      signal is the leading suspect; a small transformer/pretrained
      embedding is the next thing to try, not before this checkpoint).
- [ ] Retrain on the full merged set, save metrics.json.

**DoD:** held-out artifact_type accuracy >= 80% (a deliberately intermediate
checkpoint below the original 90% target) OR a learning-curve plot showing
the trend and a documented decision on whether to gather more data or change
architecture. Either outcome is an acceptable DoD; an unexamined plateau is
not.

## Phase 4 — Production integration

**Goal:** the distilled router serves real traffic safely, with a cheap
rollback and a quality gate the main app already trusts (the golden set).

### 4.1 Shadow mode (no user-visible change)

- [ ] `config.py`: add `router_mode: Literal["llm", "shadow", "local"] =
      "llm"`. Same pattern as the existing `artifacts_disabled` kill switch:
      one env var, no code deploy needed to change it.
- [ ] `backend/services/local_router.py`: loads `labels.json` and the
      exported model, exposes `classify(query: str) -> (Intent, confidence)`.
      Use `tflite-runtime` for the backend dependency, not full TensorFlow
      (TensorFlow is a training-time dependency in `ml/`, not a serving one;
      `tflite-runtime` is on the order of a few MB installed versus
      TensorFlow's several hundred).
- [ ] In `router_node`: when `router_mode == "shadow"`, run BOTH the LLM
      router (unchanged, still authoritative) and the local classifier.
      Record a trace row (`node="router_shadow"`) with both outputs and
      whether they agreed on artifact_type/domain/complexity. User-visible
      behavior is 100% unchanged in this mode; it only observes.
- [ ] Run shadow mode against real traffic (or against `evals/golden.yaml`
      plus a batch of logged real queries if traffic is low) for long enough
      to get a meaningful sample, not a handful of requests.

**DoD:** shadow-mode agreement rate is known and logged, computed from real
traces, not from the held-out test set (held-out numbers already exist from
Phase 3; this step is asking "does it hold on live-shaped traffic too").

### 4.2 Confidence-gated local mode

- [ ] `router_mode == "local"`: classify locally; if the top artifact_type
      softmax confidence is below a threshold (start at 0.7, tune from
      shadow-mode data), fall back to the LLM router for that request only.
      Never silently serve a low-confidence local classification.
- [ ] Extend `evals/run.py` with a `--router-mode local` flag so the golden
      set can be run against local-only routing as a regression gate.
- [ ] Gate: `router_mode=local` may only become the default after the
      golden set passes at the same bar Phase 2 of the main app uses (10/12
      artifacts route correctly, 2/12 correctly route text_only).

**DoD:** golden set passes under local routing; confidence threshold is
tuned from real shadow-mode data, not guessed.

### 4.3 Rollout, monitoring, rollback

- [ ] Default stays `router_mode=llm` until the 4.2 gate passes. Flip to
      `local` as a config change, not a deploy.
- [ ] Cost/latency dashboard (already planned for Phase 6 of the main app):
      add `router_mode` as a dimension, so the savings this track exists to
      capture are visible, not assumed.
- [ ] Rollback is `router_mode=llm`, one env var, same shape as
      `ARTIFACTS_DISABLED`. No new rollback mechanism needed; reuse the
      pattern already in the codebase.
- [ ] Model versioning: once a trained model passes the Phase 4.2 gate,
      promote it from the gitignored `ml/router-distill/out/` to a tracked
      `ml/router-distill/release/` directory (target size < 5MB, small
      enough to commit directly, no external storage needed) with a
      `MODEL_CARD.md` recording training data version, date, and the metrics
      it passed the gate with. Never let the backend load a model that
      is not committed and traceable to a specific training run.

**DoD:** `router_mode=local` is the default in `.env.example`, the golden
set is green under it, a rollback is a one-line env var change, and the
serving model is a versioned, committed artifact with a model card.

---

## Deferred: real embeddings for RAG

`ml/rag/embed.py`'s TF-IDF baseline is intentionally not swapped for a real
embedding model in this plan. Revisit only if Phase 1's retrieval smoke
tests show TF-IDF genuinely failing (missing paraphrased-but-relevant
passages, not just ranking them lower) or if the vector index size becomes
unwieldy. The interface (`fit`/`transform`) is already designed so this is a
contained swap in `embed.py` alone, not a rewrite.

## Explicit non-goals for this plan

Generating full artifact HTML from a small trained model (still out of
scope, per `router-distill/README.md`). Physics content (no source material
exists yet; Phase 1 to 3 simply have less to work with for that subject
until it arrives). Chemistry/Biology Form 5 gaps noted in the trigger table
are the same: proceed with what exists, do not block on what does not.
