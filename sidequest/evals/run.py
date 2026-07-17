"""Golden-set pipeline runner (EVALS.md sections 2 and 6).

Drives a RUNNING backend through POST /api/ask for each golden query, asserts
routing and artifact delivery, optionally runs Playwright render checks, and
appends a metrics line to evals/history.jsonl.

COSTS REAL TOKENS: roughly $1-3 for --smoke, $5-15 for the full set.

Usage:
  python run.py --smoke                 # G1, G4, G10, G12
  python run.py                         # all 12
  python run.py --only G2 --render      # one item + render check
  python run.py --base-url http://localhost:8000
"""

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

EVALS_DIR = Path(__file__).resolve().parent
ARTIFACT_TYPES_WITH_CARD = {
    "simulation",
    "explorable_diagram",
    "virtual_experiment",
    "data_visualization",
}


def ask(base_url: str, session_id: str, message: str, timeout: int = 120) -> list[tuple[str, dict]]:
    body = json.dumps({"session_id": session_id, "message": message}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/ask", data=body, headers={"Content-Type": "application/json"}
    )
    raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8")
    frames = []
    for block in raw.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.split("\n"))
        frames.append((lines["event"], json.loads(lines["data"])))
    return frames


def evaluate_item(item: dict, base_url: str, render: bool, vendor_dir: Path) -> dict:
    started = time.monotonic()
    frames = ask(base_url, f"sess-eval-{item['id'].lower()}", item["query"])
    elapsed = round(time.monotonic() - started, 2)

    names = [n for n, _ in frames]
    meta = frames[0][1]
    done = frames[-1][1]
    failures: list[str] = []

    expect = item.get("expect", {})
    routed_type = meta["intent"]["artifact_type"]
    want_type = expect.get("artifact_type")
    if want_type and routed_type != want_type:
        failures.append(f"routed {routed_type}, expected {want_type}")
    want_domains = expect.get("domain")
    if want_domains and meta["intent"]["domain"] not in want_domains:
        failures.append(f"domain {meta['intent']['domain']}, expected one of {want_domains}")

    artifact_html = None
    if want_type in ARTIFACT_TYPES_WITH_CARD or (
        want_type is None and routed_type in ARTIFACT_TYPES_WITH_CARD
    ):
        done_frames = [d for n, d in frames if n == "artifact_done"]
        failed_frames = [d for n, d in frames if n == "artifact_failed"]
        if done_frames:
            artifact_html = done_frames[0]["html"]
        else:
            failures.append(
                "no artifact_done"
                + (f" (failed: {failed_frames[0]['reason']})" if failed_frames else "")
            )
    elif want_type == "text_only":
        if "artifact_done" in names or "artifact_status" in names:
            failures.append("artifact branch ran for a text_only expectation")

    render_result = None
    if render and artifact_html:
        import render_check

        rr = render_check.check(artifact_html, vendor_dir)
        render_result = rr.__dict__ | {"passed": rr.passed}
        if not rr.passed:
            failures.append("render check failed")

    return {
        "id": item["id"],
        "query": item["query"],
        "ok": not failures,
        "failures": failures,
        "routed": meta["intent"] | {"canonical_concept": meta["canonical_concept"]},
        "artifact_bytes": len(artifact_html.encode()) if artifact_html else 0,
        "cost_usd": done.get("usage", {}).get("cost_usd", 0),
        "elapsed_s": elapsed,
        "render": render_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--smoke", action="store_true", help="run G1, G4, G10, G12 only")
    parser.add_argument("--only", help="run a single item, e.g. G2")
    parser.add_argument("--render", action="store_true", help="Playwright render checks")
    parser.add_argument(
        "--vendor-dir", default=str(EVALS_DIR.parent / "vendor"), type=Path
    )
    args = parser.parse_args()

    items = yaml.safe_load((EVALS_DIR / "golden.yaml").read_text(encoding="utf-8"))
    if args.only:
        items = [i for i in items if i["id"] == args.only]
    elif args.smoke:
        items = [i for i in items if i.get("smoke")]

    results = []
    for item in items:
        print(f"[{item['id']}] {item['query']!r} ...", flush=True)
        try:
            result = evaluate_item(item, args.base_url, args.render, args.vendor_dir)
        except Exception as exc:
            result = {"id": item["id"], "ok": False, "failures": [f"runner error: {exc}"]}
        status = "PASS" if result["ok"] else "FAIL " + "; ".join(result["failures"])
        print(f"[{item['id']}] {status}", flush=True)
        results.append(result)

    passed = sum(1 for r in results if r["ok"])
    total_cost = round(sum(r.get("cost_usd", 0) for r in results), 4)
    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "total": len(results),
        "total_cost_usd": total_cost,
        "results": results,
    }
    with (EVALS_DIR / "history.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary) + "\n")

    print(f"\n{passed}/{len(results)} passed, total cost ${total_cost}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
