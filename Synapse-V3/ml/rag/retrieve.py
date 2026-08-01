"""Query the passage index: query [+ subject/form filter] -> top-k passages.

Depends only on embed.TfidfEmbedder's fit/transform interface, so swapping
in a real embedding backend later means changing embed.py only.

Usage:
  python retrieve.py "how does osmosis work" --subject biology --form 4 --k 5
  python retrieve.py "how does osmosis work" --k 3   # no filter
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from embed import TfidfEmbedder, tokenize

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index"


def load_index() -> tuple[list[dict], np.ndarray, TfidfEmbedder]:
    passages_path = INDEX / "passages.jsonl"
    vectors_path = INDEX / "vectors.npz"
    vocab_path = INDEX / "vocab.json"
    if not (passages_path.exists() and vectors_path.exists() and vocab_path.exists()):
        raise SystemExit("index missing; run ingest.py then embed.py first")

    passages = [json.loads(line) for line in passages_path.read_text(encoding="utf-8").splitlines() if line]
    vectors = np.load(vectors_path)["vectors"]

    vocab_data = json.loads(vocab_path.read_text(encoding="utf-8"))
    embedder = TfidfEmbedder()
    embedder.vocab = vocab_data["vocab"]
    embedder.idf = np.array(vocab_data["idf"], dtype=np.float32)
    return passages, vectors, embedder


def search(
    query: str,
    passages: list[dict],
    vectors: np.ndarray,
    embedder: TfidfEmbedder,
    k: int = 5,
    subject: str | None = None,
    form: int | None = None,
) -> list[dict]:
    mask = np.ones(len(passages), dtype=bool)
    if subject:
        mask &= np.array([p["subject"] == subject for p in passages])
    if form:
        mask &= np.array([p["form"] == form for p in passages])
    if not mask.any():
        return []

    query_vec = embedder.transform([query])[0]
    scores = vectors[mask] @ query_vec
    candidates = [p for p, m in zip(passages, mask) if m]

    order = np.argsort(-scores)[:k]
    results = []
    for i in order:
        if scores[i] <= 0:
            continue  # no lexical overlap at all; not a real match
        p = dict(candidates[i])
        p["score"] = round(float(scores[i]), 4)
        results.append(p)
    return results


def main() -> None:
    # Windows terminals commonly default to cp1252, which cannot render many
    # textbook symbols (for example Δ and −). Retrieval must not fail merely
    # because a matched passage contains one of them.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--subject", choices=["biology", "chemistry", "physics"])
    parser.add_argument("--form", type=int, choices=[4, 5])
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    passages, vectors, embedder = load_index()
    if not tokenize(args.query):
        raise SystemExit("query has no indexable tokens")

    results = search(
        args.query, passages, vectors, embedder, k=args.k, subject=args.subject, form=args.form
    )
    if not results:
        print("no matches")
        return
    for r in results:
        print(f"\n[{r['score']}] {r['source_file']} chunk {r['chunk_index']} ({r['subject']} form{r['form']})")
        print(r["text"][:300] + ("..." if len(r["text"]) > 300 else ""))


if __name__ == "__main__":
    main()
