"""Build a TF-IDF vector index over index/passages.jsonl.

Pure numpy/stdlib baseline (no new heavy dependency). This is the swap
point: a real embedding backend (sentence-transformers, an API) can replace
`TfidfEmbedder` as long as it implements `.fit(texts)` and `.transform(texts)
-> np.ndarray`; retrieve.py only depends on that interface.

Usage: python embed.py
Output: index/vectors.npz, index/vocab.json
"""

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index"

_TOKEN_RE = None  # lazy import re only when needed to keep module import cheap


def tokenize(text: str) -> list[str]:
    import re

    global _TOKEN_RE
    if _TOKEN_RE is None:
        _TOKEN_RE = re.compile(r"[a-z0-9]+")
    return _TOKEN_RE.findall(text.lower())


class TfidfEmbedder:
    """Minimal from-scratch TF-IDF. Swap point for a real embedding model:
    keep the same fit/transform interface and retrieve.py needs no changes."""

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}
        self.idf: np.ndarray | None = None

    def fit(self, texts: list[str]) -> "TfidfEmbedder":
        doc_freq: Counter[str] = Counter()
        for text in texts:
            doc_freq.update(set(tokenize(text)))
        self.vocab = {term: i for i, term in enumerate(sorted(doc_freq))}
        n_docs = len(texts)
        self.idf = np.array(
            [math.log((n_docs + 1) / (doc_freq[term] + 1)) + 1 for term in self.vocab],
            dtype=np.float32,
        )
        return self

    def transform(self, texts: list[str]) -> np.ndarray:
        if self.idf is None:
            raise RuntimeError("call fit() before transform()")
        matrix = np.zeros((len(texts), len(self.vocab)), dtype=np.float32)
        for row, text in enumerate(texts):
            counts = Counter(tokenize(text))
            total = sum(counts.values()) or 1
            for term, count in counts.items():
                col = self.vocab.get(term)
                if col is not None:
                    matrix[row, col] = (count / total) * self.idf[col]
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return matrix / norms


def main() -> None:
    passages_path = INDEX / "passages.jsonl"
    if not passages_path.exists():
        raise SystemExit(f"{passages_path} missing; run ingest.py first")

    passages = [json.loads(line) for line in passages_path.read_text(encoding="utf-8").splitlines() if line]
    if not passages:
        raise SystemExit("no passages to embed; run ingest.py first")

    embedder = TfidfEmbedder().fit([p["text"] for p in passages])
    vectors = embedder.transform([p["text"] for p in passages])

    np.savez_compressed(INDEX / "vectors.npz", vectors=vectors)
    (INDEX / "vocab.json").write_text(
        json.dumps({"vocab": embedder.vocab, "idf": embedder.idf.tolist()}), encoding="utf-8"
    )
    print(f"embedded {len(passages)} passages -> {vectors.shape[1]}-dim TF-IDF vectors")
    print(f"wrote {INDEX / 'vectors.npz'} and {INDEX / 'vocab.json'}")


if __name__ == "__main__":
    main()
