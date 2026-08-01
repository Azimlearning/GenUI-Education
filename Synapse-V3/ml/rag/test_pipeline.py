"""End-to-end self-test: ingest -> embed -> retrieve, using the synthetic
placeholder in sources/_example/. Proves the wiring works with zero real
curriculum content. Run after any change to ingest.py/embed.py/retrieve.py.

Usage: python test_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run([sys.executable, *cmd], cwd=HERE)
    if result.returncode != 0:
        raise SystemExit(f"failed: {' '.join(cmd)}")


def main() -> None:
    example_dir = HERE / "sources" / "_example"
    if not example_dir.exists():
        raise SystemExit(f"{example_dir} missing; the synthetic placeholder should be checked in")

    run(["ingest.py"])
    run(["embed.py"])

    from retrieve import load_index, search

    passages, vectors, embedder = load_index()
    assert len(passages) > 0, "expected at least one chunk from the placeholder file"

    checks = [
        ("what happens to a plant cell in a hypertonic solution", "osmosis"),
        ("what is Newton's second law", "newton"),
        ("what is neutralisation between an acid and a base", "neutralis"),
    ]
    for query, expect_substring in checks:
        results = search(query, passages, vectors, embedder, k=3)
        assert results, f"no results for {query!r}"
        top_text = results[0]["text"].lower()
        assert expect_substring in top_text, (
            f"query {query!r} top result did not mention {expect_substring!r}: {top_text[:120]}"
        )
        print(f"OK  {query!r} -> top match score {results[0]['score']}, contains {expect_substring!r}")

    # filter behavior: this placeholder is tagged subject="_example" (not a
    # real subject), so a real-subject filter should return nothing.
    filtered = search("osmosis", passages, vectors, embedder, k=3, subject="biology")
    assert filtered == [], "subject filter should exclude the _example placeholder"
    print("OK  subject filter correctly excludes _example content")

    print("\nself-test passed: ingest -> embed -> retrieve wired correctly")


if __name__ == "__main__":
    main()
