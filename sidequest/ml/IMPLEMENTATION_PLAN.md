# ML Track Implementation Plan — Router Distillation + Curriculum RAG

Companion to `ml/router-distill/README.md` and `ml/rag/README.md`. Those
documents explain what exists and why; this document is what happens next,
once the full curriculum dataset is collected. Phased like `docs/PLANNING.md`
so each phase has a checklist and an explicit Definition of Done (DoD) — no
phase starts until the previous one's DoD is met, same rule as the main app.

This plan does not replace or block Axiom's own Phase 4 (Cache and Library).
It is a separate track; the two can run in parallel.

## Status: Phases 1-3 complete (2026-07-18). Phase 4 not started.

The full dataset was collected (all 6 subject/form combinations, 556MB, 17
PDFs) and Phases 1 through 3 below ran to completion the same day. Results
summarized in each phase's section; full detail in
`ml/router-distill/README.md` and `ml/rag/README.md`. Phase 4 (production
integration) is the next actual work if this track continues — it touches
the live backend, not just `ml/`, and was deliberately left for a separate
decision to start.

## Trigger and current state (historical — see Status above for what actually happened)

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

## Phase 1 — Full corpus ingestion ✅ complete

**Goal:** every supplied source file is chunked, embedded, and retrievable.

- [x] Extracted all PDFs into `ml/rag/sources/<subject>/form<N>/` (556MB, 17
      PDFs, all 6 combinations; done by the user directly before this phase
      ran, following the exact convention this plan specified).
- [x] Ran `ingest.py` at full scale: 1971 passages, 10m4s for 556MB. 4 files
      (Chemistry's dedicated experiment/activity books, both forms) failed
      with zero extractable text — confirmed scanned/image PDFs (one image
      per page, no text layer), not a pypdf bug. No Tesseract OCR engine
      available on this machine; installing one is a system-level change,
      not made here. Partial mitigation: the general Chemistry textbooks
      (which did extract) contain embedded experiments in the same format.
- [x] Spot-checked extraction quality across all 6 combos: clean, readable
      text throughout, including "KEMENTERIAN PENDIDIKAN MALAYSIA" headers
      confirming authentic official textbooks. Minor cosmetic encoding
      artifacts only (`°C` -> `�C`), as anticipated.
- [x] Ran `embed.py`: 1.8MB vectors.npz, seconds not minutes. No pressure to
      swap the TF-IDF baseline yet on size/speed grounds.
- [x] Ran smoke queries per subject/form combo. 4/6 strong on the first try.
      2/6 (biology_form5, chemistry_form5) initially looked weak — resolved
      in Phase 2 below as a topic-taxonomy error, not a retrieval defect.

**DoD met**, with the 4-file OCR gap and the Phase-2-resolved smoke-query
story both documented rather than glossed over.

## Phase 2 — Topic grounding ✅ complete

**Goal:** `kssm_topics.py` reflects real curriculum content, not general
knowledge.

- [x] Extracted tables of contents via `extract_toc.py` (new script, not
      anticipated by name in the original plan text but exactly the
      described strategy: outline-first, pattern-match fallback). Biology
      and Physics textbooks had clean, complete, chapter-numbered outlines;
      Chemistry's gave messier pattern-matched headings (noted as
      lower-confidence in `kssm_topics.py`'s comments).
- [x] Diffed against the hand-drafted list. Found systematic, not minor,
      errors: Biology's Coordination/Nervous/Endocrine System is Form 4
      (real chapter 12), not Form 5 as guessed; 3 whole Form 4 chapters were
      missing (Circulatory System, Immunity, Homeostasis/Urinary); Physics
      had Waves/Light and Forces/Pressure/Elasticity in the WRONG forms,
      swapped relative to the real curriculum, plus two missing chapters
      (circular motion/gravitation in Form 4, quantum physics in Form 5);
      Chemistry's Rate of Reaction/Collision Theory is Form 4, not Form 5.
- [x] **Human review completed.** Full diff presented via AskUserQuestion
      with concrete before/after examples; "apply the full correction now"
      approved explicitly before `kssm_topics.py` was touched.
- [x] Re-verified the 2 biology experiment PDFs (amylase, yeast
      fermentation): their page numbers (p.92, p.120) match exactly against
      the Biology Form 4 experiment book's own table of contents. Confirmed
      correctly placed in Form 4; no move needed.
- [x] All 6 combinations now have real source material (the trigger table
      above is out of date; see Status at the top of this document).
- [x] **Round 3 addendum:** an independently-produced topic-grounding report
      (contents-page reading, different method) was found unstaged partway
      through Phase 3 and cross-checked against this phase's v2 correction.
      It confirmed the major placement fixes and caught 4 more errors v2
      missed (2 entire missing Biology Form 4 chapters, 1 chemistry
      form-placement conflict, 1 unrecognized distinct chapter). Applied as
      `kssm_topics.py` v3 (50 -> 53 topics). Lesson: a second independent
      extraction method is genuinely worth doing before calling topic
      grounding complete, not just a nice-to-have.

**DoD met.** `kssm_topics.py` went from 40 topics (hand-drafted) to 50
(grounded, with comments citing the source file and page/chapter evidence
for each corrected entry).

## Phase 3 — Grounded dataset regeneration and retraining ✅ complete

**Goal:** a router-distill dataset written in real curriculum register,
sized enough to test whether Phase 1 (README) findings hold ("data volume
is the bottleneck") or whether an architecture change is also needed.

- [x] Re-ran `generate_curriculum_dataset.py` against the corrected 50-topic
      list: 1516 new rows (`--tag kssm2 --per-style 6`, up from the previous
      round's `--per-style 3`). Confirmed via AskUserQuestion before
      spending (topic count grew materially past 40, the plan's own
      pre-set trigger for a check-in).
- [x] Built retrieval-anchored generation (`grounding_excerpt()` in
      `generate_curriculum_dataset.py`): one real passage per topic, fetched
      once and reused across all 5 styles, included in the generation
      prompt. 50/50 topics matched a real passage. Falls back to topic-only
      generation on any retrieval failure, never hard-fails a run. Kept
      small and isolated as specified: it's one new function plus one
      template string, easy to disable with `--no-grounding`.
- [x] Generated at `--per-style 6`: 1516 rows, cost stayed in the estimated
      $2-4 range (5m38s runtime, fast model).
- [x] Ran `prepare_dataset.py`, merging v1 + kssm1 (uncorrected-topic
      curriculum round) + kssm2 (corrected-topic, grounded round): 2573
      total rows, 2058 train / 514 held-out. kssm1's `curriculum_topic` tags
      are now stale against `kssm_topics.py` v2 (the slugs changed) but its
      query/label pairs remain valid training signal, so it was kept rather
      than discarded.
- [x] Ran the learning-curve check (`learning_curve.py`, new script):
      25/50/75/100% of training data, same architecture. Result is NOT a
      uniform "more data helps" story: domain accuracy rose cleanly and
      consistently (71.4% -> 85.6%, +14.2 points, clearly still data-bound).
      artifact_type accuracy jumped 25%->50% (+6.6) then plateaued/noisy
      50%->100% (70.0 -> 68.7 -> 70.4). Full numbers and the documented
      decision (different treatment for domain vs artifact_type going
      forward) are in `ml/router-distill/README.md`.
- [x] Retrained on the full merged set: artifact_type 70.4%, domain 88.1%
      (within 4 points of the 92% target), complexity 78.6%, text_only
      recall 84.8%. `out/metrics.json` and `out/learning_curve.json`.

**DoD met via the learning-curve-and-documented-decision path** (the
intermediate 80% artifact_type checkpoint was NOT hit — 70.4% — but per the
plan's own "either outcome is acceptable" rule, a real learning curve with a
non-obvious, subject-specific finding satisfies the DoD; an unexamined
plateau would not have).

**Round 3 addendum (same day):** the Phase 2 round-3 topic corrections (see
above) required closing the gap in the training data too. Rather than a
full 53-topic re-generation, added a `--topics-contains` filter to
`generate_curriculum_dataset.py` for a targeted top-up: 120 rows across
exactly the 4 changed topics (~$0.20-0.40). Final dataset 2693 rows (2154
train / 538 held-out); metrics moved little (artifact_type 69.3%, domain
86.4%, complexity 76.8%, text_only recall 80.3%), consistent with the
plateau finding rather than contradicting it. This round's value was
curriculum correctness, not an accuracy gain — recorded honestly rather
than as a regression, since the previous numbers were computed on data with
two real chapters entirely missing.

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
