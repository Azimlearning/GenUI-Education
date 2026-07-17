"""Chunk source files under sources/<subject>/form<N>/ into passages.

Supports .txt, .md (read directly) and .pdf (via pypdf, optional dependency).
Chunks are ~300 words with 50-word overlap, so a fact split across a chunk
boundary is still retrievable from at least one chunk.

Usage: python ingest.py [--skip-example] [--words-per-chunk 300] [--overlap 50]
Output: index/passages.jsonl
"""

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
INDEX = HERE / "index"

VALID_SUBJECTS = {"biology", "chemistry", "physics"}


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_pdf_file(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit(
            "pypdf required for PDF sources: pip install -r requirements.txt"
        ) from exc
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_source(path: Path) -> str:
    if path.suffix.lower() in (".txt", ".md"):
        return read_text_file(path)
    if path.suffix.lower() == ".pdf":
        return read_pdf_file(path)
    raise ValueError(f"unsupported source type: {path.suffix}")


def chunk_words(words: list[str], size: int, overlap: int) -> list[list[str]]:
    if size <= overlap:
        raise ValueError("chunk size must exceed overlap")
    chunks = []
    step = size - overlap
    for start in range(0, max(len(words), 1), step):
        chunk = words[start : start + size]
        if chunk:
            chunks.append(chunk)
        if start + size >= len(words):
            break
    return chunks


def infer_subject_form(path: Path) -> tuple[str, int] | None:
    """Path shape: sources/<subject>/form<N>/<file>."""
    try:
        rel = path.relative_to(SOURCES)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 3:
        return None
    subject, form_dir = parts[0], parts[1]
    match = re.fullmatch(r"form(\d)", form_dir)
    if subject not in VALID_SUBJECTS or not match:
        return None
    return subject, int(match.group(1))


def ingest(words_per_chunk: int, overlap: int, skip_example: bool) -> list[dict]:
    passages = []
    for path in sorted(SOURCES.rglob("*")):
        if not path.is_file():
            continue
        if skip_example and "_example" in path.parts:
            continue
        subject_form = infer_subject_form(path)
        is_example = "_example" in path.parts
        if subject_form is None and not is_example:
            print(f"skip (not under sources/<subject>/form<N>/): {path}")
            continue
        subject, form = subject_form if subject_form else ("_example", 0)

        try:
            text = load_source(path)
        except Exception as exc:
            print(f"skip (read failed: {exc}): {path}")
            continue

        words = text.split()
        if not words:
            print(f"skip (no extractable text): {path}")
            continue

        for i, chunk in enumerate(chunk_words(words, words_per_chunk, overlap)):
            passages.append(
                {
                    "text": " ".join(chunk),
                    "subject": subject,
                    "form": form,
                    "source_file": str(path.relative_to(SOURCES)),
                    "chunk_index": i,
                }
            )
    return passages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--words-per-chunk", type=int, default=300)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument("--skip-example", action="store_true")
    args = parser.parse_args()

    passages = ingest(args.words_per_chunk, args.overlap, args.skip_example)

    INDEX.mkdir(parents=True, exist_ok=True)
    out = INDEX / "passages.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    by_combo: dict[str, int] = {}
    for p in passages:
        key = f"{p['subject']}_form{p['form']}" if p["subject"] != "_example" else "_example"
        by_combo[key] = by_combo.get(key, 0) + 1
    print(f"wrote {len(passages)} passages to {out}")
    print("by subject/form:", dict(sorted(by_combo.items())))


if __name__ == "__main__":
    main()
