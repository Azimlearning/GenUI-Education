"""Full-stack UI smoke: drive the real chat page in headless Chromium.

Types a question into the running frontend, waits for streamed text, then (if
an artifact is expected) waits for the sandboxed iframe and asserts the bridge
delivered axiom_ready (the card's opacity transition completes and controls
exist inside the frame).

Usage: python ui_smoke.py [--url http://localhost:3000] [--query "..."] [--expect-artifact]
"""

import argparse
import json


def main() -> int:
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:3000")
    parser.add_argument("--query", default="show me projectile motion")
    parser.add_argument("--expect-artifact", action="store_true")
    parser.add_argument("--screenshot", help="save a PNG here at the end")
    parser.add_argument("--timeout-s", type=int, default=120)
    args = parser.parse_args()

    result = {"text_streamed": False, "artifact_ready": False, "console_errors": []}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 900, "height": 1000})
        page.on(
            "console",
            lambda m: result["console_errors"].append(m.text) if m.type == "error" else None,
        )

        page.goto(args.url)
        box = page.get_by_role("textbox", name="Your science question")
        box.fill(args.query)
        box.press("Enter")

        # Streamed text: the assistant paragraph accumulates characters.
        page.wait_for_function(
            "document.body.innerText.length > 400", timeout=args.timeout_s * 1000
        )
        result["text_streamed"] = True

        if args.expect_artifact:
            frame_el = page.wait_for_selector(
                "iframe[sandbox='allow-scripts']", timeout=args.timeout_s * 1000
            )
            # axiom_ready flips the frame's opacity from 0.4 to 1.
            page.wait_for_function(
                "el => getComputedStyle(el).opacity === '1'",
                arg=frame_el,
                timeout=15_000,
            )
            frame = frame_el.content_frame()
            controls = frame.query_selector_all("input[type=range], select, button")
            result["artifact_ready"] = len(controls) > 0
            result["controls_in_artifact"] = len(controls)

        if args.screenshot:
            page.wait_for_timeout(500)
            page.screenshot(path=args.screenshot, full_page=True)
        browser.close()

    print(json.dumps(result, indent=2))
    ok = result["text_streamed"] and (result["artifact_ready"] or not args.expect_artifact)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
