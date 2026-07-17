"""Playwright render checks for one artifact (EVALS.md section 4).

Mounts the artifact exactly as production does: an iframe with
sandbox="allow-scripts" and srcdoc, inside a parent page that listens for
bridge messages. v1 asserts:

  1. axiom_ready received within 5s
  2. zero forbidden-API strings in the final HTML (same scan as postprocess.py)
  3. at least one control present, and dispatching input to it mutates the
     artifact (screenshot diff) within 1s
  4. no uncaught page errors during a short scripted interaction

Memory budget and reset-restores-default checks arrive in Phase 2.

Usage: python render_check.py <artifact.html> [--vendor-dir ../vendor]
"""

import argparse
import http.server
import json
import re
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
import postprocess  # noqa: E402  (single source of truth for the deny list)

HARNESS = """
<!doctype html><html><head><meta charset="utf-8"></head><body>
<script>
  window.__axiom = { ready: false, errors: [], events: [] };
  window.addEventListener("message", (e) => {
    const d = e.data || {};
    if (d.type === "axiom_ready") window.__axiom.ready = true;
    if (d.type === "axiom_error") window.__axiom.errors.push(String(d.message));
    if (d.type === "axiom_event") window.__axiom.events.push(d);
  });
</script>
<iframe id="artifact" sandbox="allow-scripts" style="width:420px;height:640px;border:0"></iframe>
<script>
  document.getElementById("artifact").srcdoc = __ARTIFACT_HTML__;
</script>
</body></html>
"""


@dataclass
class RenderResult:
    ready: bool = False
    forbidden: list = field(default_factory=list)
    control_found: bool = False
    control_wired: bool = False
    page_errors: list = field(default_factory=list)
    artifact_errors: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.ready
            and not self.forbidden
            and self.control_found
            and self.control_wired
            and not self.page_errors
            and not self.artifact_errors
        )


def _serve_vendor(vendor_dir: Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    """Serve /vendor/* the way the app does, so artifact script tags resolve."""
    root = vendor_dir.parent

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def check(html: str, vendor_dir: Path) -> RenderResult:
    from playwright.sync_api import sync_playwright

    result = RenderResult()

    # The platform-injected CSP meta contains the app origin literal by design
    # (SECURITY.md section 2.3); strip OUR tag before scanning so the scan
    # covers exactly the model-authored content.
    scannable = re.sub(
        r"<meta\b[^>]*http-equiv\s*=\s*[\"']Content-Security-Policy[\"'][^>]*>",
        "",
        html,
        flags=re.IGNORECASE,
    )
    scan = postprocess.forbidden_api_scan(scannable)
    if isinstance(scan, postprocess.PostprocessReject):
        result.forbidden.append(scan.reason)

    server, port = _serve_vendor(vendor_dir)
    # The artifact's CSP names the configured public origin (localhost:3000);
    # the harness serves /vendor from its own ephemeral origin, so re-point the
    # CSP exactly as postprocess would have for this origin. The forbidden scan
    # guarantees the only absolute URL in the document is our injected one.
    html = html.replace("http://localhost:3000", f"http://127.0.0.1:{port}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 480, "height": 800})
            page.on("pageerror", lambda e: result.page_errors.append(str(e)))

            # Serve the harness from the same origin as /vendor/* so the
            # artifact's relative script tags resolve, exactly like production.
            # `</` must be escaped or the artifact's own </script> closes the
            # harness script tag mid-string.
            payload = json.dumps(html).replace("</", "<\\/")
            harness = HARNESS.replace("__ARTIFACT_HTML__", payload)
            page.route(
                f"http://127.0.0.1:{port}/harness",
                lambda route: route.fulfill(content_type="text/html", body=harness),
            )
            page.goto(f"http://127.0.0.1:{port}/harness")

            try:
                page.wait_for_function("window.__axiom.ready === true", timeout=5000)
                result.ready = True
            except Exception:
                result.ready = False

            frame = page.frame_locator("#artifact")
            controls = frame.locator(
                "input[type=range], input[type=number], select, button:not([id=reset])"
            )
            count = controls.count()
            result.control_found = count > 0

            if result.ready and result.control_found:
                before = page.locator("#artifact").screenshot()
                slider = frame.locator("input[type=range]").first
                if slider.count() > 0:
                    slider.evaluate(
                        "el => { el.value = el.max; "
                        "el.dispatchEvent(new Event('input', {bubbles:true})); }"
                    )
                else:
                    controls.first.click()
                page.wait_for_timeout(1000)
                after = page.locator("#artifact").screenshot()
                result.control_wired = before != after

            result.artifact_errors = page.evaluate("window.__axiom.errors")
            browser.close()
    finally:
        server.shutdown()

    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    parser.add_argument(
        "--vendor-dir", default=str(Path(__file__).resolve().parent.parent / "vendor")
    )
    args = parser.parse_args()

    html = Path(args.html_file).read_text(encoding="utf-8")
    result = check(html, Path(args.vendor_dir))
    print(json.dumps(result.__dict__ | {"passed": result.passed}, indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
