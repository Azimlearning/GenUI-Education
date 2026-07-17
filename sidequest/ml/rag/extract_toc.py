"""Extract table-of-contents / heading structure from each source PDF.

Two strategies, tried in order per file:
1. PDF navigable outline (bookmarks), via pypdf's reader.outline. Clean when
   present, but many scanned/exported textbooks have none.
2. Heading-pattern matching over the first ~15% of extracted pages: lines
   that look like "5.1 Something", "Bab 7", "Chapter 3", "CHAPTER 3", etc.
   Heuristic, meant to be human-reviewed, not trusted blindly (see
   IMPLEMENTATION_PLAN.md Phase 2: human review required before merging
   anything derived from this into kssm_topics.py).

Usage: python extract_toc.py
Output: index/toc_report.json — one entry per source file, with whichever
strategy succeeded and how many candidate headings were found.
"""

import json
import re
from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
INDEX = HERE / "index"

HEADING_PATTERNS = [
    re.compile(r"^\s*(\d{1,2}\.\d{1,2})\s+([A-Z][A-Za-z0-9 ,\-'()]{4,80})\s*$"),  # "5.1 Cell Division"
    re.compile(r"^\s*(BAB|Bab)\s+(\d{1,2})\s*[:\-]?\s*(.{0,80})\s*$"),  # Malay: "Bab 7: ..."
    re.compile(r"^\s*(CHAPTER|Chapter)\s+(\d{1,2})\s*[:\-]?\s*(.{0,80})\s*$"),
    re.compile(r"^\s*(TEMA|Tema)\s+(\d{1,2})\s*[:\-]?\s*(.{0,80})\s*$"),  # Malay curriculum "Theme"
]


def outline_headings(reader: PdfReader) -> list[str]:
    def walk(items) -> list[str]:
        out = []
        for item in items:
            if isinstance(item, list):
                out.extend(walk(item))
            else:
                title = getattr(item, "title", None)
                if title:
                    out.append(str(title).strip())
        return out

    try:
        return walk(reader.outline)
    except Exception:
        return []


def pattern_headings(reader: PdfReader, max_page_fraction: float = 0.15) -> list[str]:
    n_pages = len(reader.pages)
    scan_pages = max(5, int(n_pages * max_page_fraction))
    found = []
    for page in reader.pages[:scan_pages]:
        try:
            text = page.extract_text() or ""
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for pattern in HEADING_PATTERNS:
                if pattern.match(line):
                    found.append(line)
                    break
    # Dedupe while preserving order.
    seen = set()
    unique = []
    for h in found:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique


def infer_subject_form(path: Path) -> tuple[str, int] | None:
    try:
        rel = path.relative_to(SOURCES)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 3:
        return None
    match = re.fullmatch(r"form(\d)", parts[1])
    if not match:
        return None
    return parts[0], int(match.group(1))


def main() -> None:
    report = []
    for path in sorted(SOURCES.rglob("*.pdf")):
        subject_form = infer_subject_form(path)
        if subject_form is None:
            continue
        subject, form = subject_form

        try:
            reader = PdfReader(str(path))
        except Exception as exc:
            report.append(
                {
                    "source_file": str(path.relative_to(SOURCES)),
                    "subject": subject,
                    "form": form,
                    "error": str(exc),
                }
            )
            print(f"FAILED to open: {path.name}: {exc}")
            continue

        outline = outline_headings(reader)
        strategy = "outline" if outline else "pattern"
        headings = outline if outline else pattern_headings(reader)

        report.append(
            {
                "source_file": str(path.relative_to(SOURCES)),
                "subject": subject,
                "form": form,
                "n_pages": len(reader.pages),
                "strategy": strategy,
                "n_headings": len(headings),
                "headings": headings,
            }
        )
        print(f"{path.name}: {len(reader.pages)} pages, {strategy} strategy, {len(headings)} headings found")

    INDEX.mkdir(parents=True, exist_ok=True)
    out = INDEX / "toc_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out}")
    print(
        "REMINDER (IMPLEMENTATION_PLAN.md Phase 2): this is a heuristic extraction. "
        "Human review required before updating kssm_topics.py from it."
    )


if __name__ == "__main__":
    main()
