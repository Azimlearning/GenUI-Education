#!/usr/bin/env python3
"""Verify vendored libraries against CHECKSUMS.txt (SECURITY.md T9: supply chain).

Run in CI on every build:      python vendor/verify.py
Rewrite after a deliberate
version bump (review the diff): python vendor/verify.py --write
"""

import hashlib
import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parent
CHECKSUMS = VENDOR / "CHECKSUMS.txt"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_files() -> list[Path]:
    files = sorted(VENDOR.glob("*.js")) + sorted(VENDOR.glob("*.css"))
    files += sorted((VENDOR / "fonts").glob("*.woff2"))
    return files


def read_expected() -> dict[str, str]:
    expected: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        sha, name = line.split(None, 1)
        expected[name.strip()] = sha
    return expected


def main() -> int:
    if "--write" in sys.argv:
        header = [
            line
            for line in CHECKSUMS.read_text(encoding="utf-8").splitlines()
            if line.startswith("#") or not line.strip()
        ]
        body = [
            f"{digest(p)} {p.relative_to(VENDOR).as_posix()}" for p in tracked_files()
        ]
        CHECKSUMS.write_text("\n".join(header + body) + "\n", encoding="utf-8")
        print(f"wrote {len(body)} checksums to {CHECKSUMS.name}")
        return 0

    expected = read_expected()
    actual = {p.relative_to(VENDOR).as_posix(): digest(p) for p in tracked_files()}

    problems: list[str] = []
    for name, sha in expected.items():
        if name not in actual:
            problems.append(f"MISSING  {name}")
        elif actual[name] != sha:
            problems.append(f"MISMATCH {name}\n  expected {sha}\n  actual   {actual[name]}")
    for name in actual:
        if name not in expected:
            problems.append(f"UNTRACKED {name} (not in CHECKSUMS.txt)")

    if problems:
        print("vendor verification FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print(f"vendor verification OK ({len(actual)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
