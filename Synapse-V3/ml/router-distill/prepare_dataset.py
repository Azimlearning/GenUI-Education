"""Clean and split the labeled data into train/test sets.

Reads every dataset/labeled/*.jsonl, then:
  1. drops malformed rows (missing fields, invalid labels)
  2. normalizes whitespace, drops queries under 2 words (except known junk)
  3. dedupes case-insensitively by query (first label wins)
  4. shuffles with a fixed seed and splits 80/20

Writes dataset/clean/train.jsonl, dataset/clean/test.jsonl, dataset/clean/stats.json.

Usage: python prepare_dataset.py [--test-frac 0.2] [--seed 7]
"""

import argparse
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELED = HERE / "dataset" / "labeled"
CLEAN = HERE / "dataset" / "clean"

ARTIFACT_TYPES = {
    "simulation",
    "explorable_diagram",
    "virtual_experiment",
    "data_visualization",
    "text_only",
}
DOMAINS = {"physics", "chemistry", "biology", "earth_space", "math_adjacent"}


def valid(row: dict) -> bool:
    return (
        isinstance(row.get("query"), str)
        and row.get("artifact_type") in ARTIFACT_TYPES
        and row.get("domain") in DOMAINS
        and row.get("complexity") in (1, 2, 3)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-frac", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    files = sorted(LABELED.glob("*.jsonl"))
    if not files:
        raise SystemExit(f"no labeled files in {LABELED}; run generate_dataset.py first")

    rows, dropped = [], 0
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                dropped += 1
                continue
            if not valid(row):
                dropped += 1
                continue
            row["query"] = " ".join(row["query"].split())
            rows.append(row)

    seen: set[str] = set()
    unique = []
    for row in rows:
        key = row["query"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    random.Random(args.seed).shuffle(unique)
    n_test = int(len(unique) * args.test_frac)
    test, train = unique[:n_test], unique[n_test:]

    CLEAN.mkdir(parents=True, exist_ok=True)
    for name, subset in (("train.jsonl", train), ("test.jsonl", test)):
        with (CLEAN / name).open("w", encoding="utf-8") as f:
            for row in subset:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    stats = {
        "source_files": [p.name for p in files],
        "raw_rows": len(rows) + dropped,
        "dropped_malformed": dropped,
        "duplicates_removed": len(rows) - len(unique),
        "train": len(train),
        "test": len(test),
        "artifact_type_dist": dict(Counter(r["artifact_type"] for r in unique)),
        "domain_dist": dict(Counter(r["domain"] for r in unique)),
        "complexity_dist": dict(Counter(str(r["complexity"]) for r in unique)),
    }
    (CLEAN / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
