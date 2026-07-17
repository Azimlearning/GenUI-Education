# Curriculum RAG

Retrieval pipeline to ground the Planner/Generator (and later the dataset
generators in `ml/router-distill/`) in real KSSM Form 4/5 textbook or syllabus
text, instead of the hand-drafted `kssm_topics.py` topic list.

**For ingesting the full dataset once collected** (all 6 subject/form
combinations, topic grounding, downstream regeneration), see
[`../IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md).

## Status (2026-07-18, full corpus ingested)

All 6 subject/form combinations now have real source material (556MB, 17
PDFs) under `sources/`, and the full pipeline has been run end to end. See
`../IMPLEMENTATION_PLAN.md` Phase 1 for the checklist this satisfies.

**Ingestion:** 1971 passages across all 6 combos (285 to 377 each). 4 files
failed extraction with zero text: `Aktiviti _ Eksperimen Kimia.pdf` and
`Experiment _ Activity Chemistry(.pdf/2.pdf)` in both chemistry/form4 and
chemistry/form5. Confirmed these are scanned/image PDFs (one image per page,
no text layer), not a pypdf bug. No Tesseract OCR engine is available on
this machine and installing one is a system-level change, not made here.
**These 4 files (the dedicated chemistry experiment/activity books, both
forms) are not in the index.** Partial mitigation: `CHEMISTRY F4.pdf` and
`CHEMISTRY F5.pdf` (the general textbooks, which DID extract) contain
embedded experiments in the same Problem/Hypothesis/Variables format, so
chemistry experiment content is reduced, not absent.

**Retrieval quality, honestly evaluated with smoke queries per combo:**
4 of 6 (biology_form4, chemistry_form4, physics_form4, physics_form5) return
strong, correct top-1 matches (scores 0.45 to 0.48). 2 of 6 initially did
not: `biology_form5` queries about human nervous/endocrine coordination kept
surfacing plant hormone content, and `chemistry_form5` queries about
reaction rate kept surfacing thermochemistry content.

**Correction (2026-07-18, Phase 2 topic grounding):** this was NOT a TF-IDF
ranking failure. Extracting the real tables of contents (`extract_toc.py`)
showed the hand-drafted topic taxonomy had those topics in the wrong form
entirely: human Coordination and Response is a Form 4 chapter, not Form 5
(Biology Form 5's real content is almost entirely plant biology, genetics,
and ecosystems, with no human nervous-system chapter at all), and
Collision Theory is a Form 4 chapter (CHEMISTRY F4.pdf, "7.4 Collision
Theory", p.243), not Form 5. The smoke queries were testing the wrong
hypothesis, not exposing a retrieval defect. `kssm_topics.py` v2 corrects
this; see `ml/router-distill/README.md`.

This does NOT mean TF-IDF's lexical-only limitation is a non-issue in
general (same-word-different-topic confusion is a real, documented category
of failure for pure keyword matching) — only that THIS specific piece of
evidence for it was invalid. The "Deferred: real embeddings" section below
still stands as a real future consideration, just without this false
positive backing it. Re-evaluate retrieval quality against the corrected
topic list before citing a fresh example.

Nothing here is used by the live Axiom backend or the router-distill
dataset generators yet; wiring that in is future work, listed at the bottom.

## Why a from-scratch TF-IDF baseline, not embeddings

Semantic embedding retrieval (sentence-transformers or an embeddings API)
is the eventual right answer, but it is a new, heavy dependency (~500MB with
torch) or a new external API surface, and there is no content to retrieve
yet either way. `retrieve.py` ships a pure numpy/stdlib TF-IDF + cosine
baseline: zero new dependencies, exact and fast at the scale one classroom's
worth of textbooks reaches, and it defines the retrieval interface
(`embed(texts) -> vectors`, `search(query, k) -> passages`) that a real
embedding backend can drop into later without changing callers. Swap point
is `embed.py`; nothing else needs to change.

## Layout

```
ml/rag/
├── sources/                  # drop textbook/syllabus files here, organized
│   ├── biology/form4/        # by subject/form so ingest.py can tag
│   ├── biology/form5/        # provenance automatically
│   ├── chemistry/form4/
│   ├── chemistry/form5/
│   ├── physics/form4/
│   └── physics/form5/
├── ingest.py                 # sources/**/*.{txt,md,pdf} -> chunked passages
├── embed.py                  # passages -> TF-IDF vectors (swap point for real embeddings)
├── retrieve.py               # query [+ subject/form filter] -> top-k passages
├── index/                    # gitignored: built artifacts (passages.jsonl, vectors.npz, vocab.json)
└── test_pipeline.py          # end-to-end self-test on a synthetic example, no real content needed
```

## Adding a real source

1. Drop the file (`.txt`, `.md`, or `.pdf`) into `sources/<subject>/form<N>/`.
   Filename becomes part of the citation; name it something recognizable
   (`kssm_biology_f4_chapter3_cell_division.pdf`).
2. `python ingest.py` — re-chunks everything in `sources/`, writes
   `index/passages.jsonl` with `{text, subject, form, source_file, chunk_index}`.
3. `python embed.py` — builds `index/vectors.npz` + `index/vocab.json` from
   the current passages.
4. `python retrieve.py "your query" --subject biology --form 4 --k 5` to
   sanity-check retrieval before wiring it into anything.

PDF extraction needs `pypdf` (`pip install -r requirements.txt`); `.txt`/`.md`
sources need nothing extra.

## Self-test (no real content required)

```
python test_pipeline.py
```

Ingests, embeds, and retrieves over a small synthetic example
(`sources/_example/`, clearly marked as non-curriculum placeholder text) to
prove the wiring end to end. Delete `sources/_example/` once real content
exists; `ingest.py` skips it if `--skip-example` is passed.

## Future integration points (not built yet)

- **`kssm_topics.py` grounding**: once real syllabus specification documents
  are ingested, regenerate the topic list from retrieved learning-standard
  text instead of the hand-drafted version, and diff the two.
- **Generator/Planner grounding**: retrieve top-k passages for a query's
  `curriculum_topic` and pass them into the Planner prompt as additional
  context, so governing models and terminology match the actual syllabus
  register instead of general scientific English.
- **Citation surfacing**: if grounded, the artifact's "Try this" hint or a
  new UI element could cite the source chapter, which is a genuine
  trust-building feature for a curriculum-aligned product.

None of this is implemented; each needs real source content first.
