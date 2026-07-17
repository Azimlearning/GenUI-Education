import { describe, expect, test } from "bun:test";
import { buildSrcdoc, extractHtml, validateGenerated } from "../sandbox";

const GOOD = `<!DOCTYPE html><html><head><title>Pendulum</title></head><body>
<div class="card"><h1>Pendulum</h1><canvas id="c"></canvas>
<label>Length<input type="range" id="len" min="0.1" max="2" value="1"></label>
<button onclick="run()">Run</button></div>
<script>function run(){ reportEvent("ran", { len: 1 }); }</script>
</body></html>`;

describe("extractHtml", () => {
  test("passes a bare document through", () => {
    expect(extractHtml(GOOD)).toBe(GOOD);
  });

  test("unwraps a fenced document", () => {
    expect(extractHtml("```html\n" + GOOD + "\n```")).toBe(GOOD);
  });

  test("drops prose before the document", () => {
    const out = extractHtml("Sure! Here's your lab:\n\n" + GOOD);
    expect(out.startsWith("<!DOCTYPE html>")).toBe(true);
  });
});

describe("validateGenerated", () => {
  test("accepts a well-formed self-contained lab", () => {
    expect(validateGenerated(GOOD)).toEqual({ ok: true, errors: [] });
  });

  // Every one of these renders a dead lab inside the sandbox, so they must fail
  // into the fallback chain rather than reach the screen.
  const rejected: [string, string][] = [
    ["<script src>", GOOD.replace("<script>", '<script src="https://cdn.jsdelivr.net/npm/p5"></script><script>')],
    ["external stylesheet", GOOD.replace("<head>", '<head><link rel="stylesheet" href="https://fonts.googleapis.com/css">')],
    ["fetch", GOOD.replace("function run(){", 'function run(){ fetch("/api/x");')],
    ["XMLHttpRequest", GOOD.replace("function run(){", "function run(){ new XMLHttpRequest();")],
    ["remote image", GOOD.replace("<canvas", '<img src="https://example.com/a.png"><canvas')],
    ["localStorage", GOOD.replace("function run(){", 'function run(){ localStorage.setItem("a","b");')],
    ["CSS @import", GOOD.replace("<head>", "<head><style>@import url(https://x.com/a.css);</style>")],
  ];

  for (const [label, html] of rejected) {
    test(`rejects ${label}`, () => {
      const result = validateGenerated(html);
      expect(result.ok).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  }

  test("rejects a document with no script as non-interactive", () => {
    const inert = "<!DOCTYPE html><html><body><p>" + "x".repeat(300) + "</p></body></html>";
    expect(validateGenerated(inert).ok).toBe(false);
  });

  test("rejects a stub", () => {
    expect(validateGenerated("<html></html>").ok).toBe(false);
  });
});

describe("buildSrcdoc", () => {
  test("injects the CSP, the design tokens and the event bridge", () => {
    const doc = buildSrcdoc(GOOD);
    expect(doc).toContain("Content-Security-Policy");
    expect(doc).toContain("default-src 'none'");
    expect(doc).toContain("--accent");
    expect(doc).toContain("window.reportEvent");
  });

  test("puts the CSP inside head, before the generated content", () => {
    const doc = buildSrcdoc(GOOD);
    expect(doc.indexOf("Content-Security-Policy")).toBeLessThan(doc.indexOf("<body"));
  });

  test("puts the bridge before </body> so generated scripts can call it", () => {
    const doc = buildSrcdoc(GOOD);
    expect(doc.indexOf("window.reportEvent")).toBeLessThan(doc.lastIndexOf("</body>"));
  });

  test("still injects when the document has no head", () => {
    const headless = "<html><body><script>reportEvent('x',{})</script></body></html>";
    const doc = buildSrcdoc(headless);
    expect(doc).toContain("Content-Security-Policy");
    expect(doc).toContain("window.reportEvent");
  });

  test("the CSP permits no network egress", () => {
    const csp = buildSrcdoc(GOOD).match(/content="([^"]+)"/)?.[1] ?? "";
    expect(csp).toContain("default-src 'none'");
    expect(csp).not.toContain("connect-src");
    expect(csp).not.toContain("https:");
  });
});
