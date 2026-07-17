/**
 * Tier C: the escape hatch, and the rules that keep it safe.
 *
 * The non-negotiable rule, consistent with every implementation surveyed in
 * ../research/generative-ui-research-2026-07-06.md §6.2:
 *
 *     GENERATED CODE NEVER TOUCHES THE HOST DOM.
 *
 * It runs inside <iframe sandbox="allow-scripts"> with no allow-same-origin, so
 * it gets an opaque origin: no access to our cookies, storage, or document. A
 * CSP inside the frame blocks network egress. Interactions come back only
 * through postMessage, which we treat as untrusted input.
 *
 * Note on the sandbox attribute: allow-scripts WITHOUT allow-same-origin is the
 * load-bearing combination. Granting both together would let the frame reach
 * out and remove its own sandbox attribute from the parent.
 */

/** Design tokens injected into every sandbox, so generated labs look like Synapse. */
export const SANDBOX_TOKENS = `
:root {
  --bg: #0b0e14; --surface: #131722; --surface-2: #1a2030; --border: #262e42;
  --text: #e6e9f0; --muted: #8b93a7; --accent: #6c8cff; --accent-strong: #4d6fff;
  --success: #34c98e; --warning: #e8b339; --danger: #f26d6d; --radius: 10px;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #f7f8fa; --surface: #ffffff; --surface-2: #f0f2f6; --border: #dfe3ec;
    --text: #131722; --muted: #5c6479;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 16px; background: var(--bg); color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  line-height: 1.5; font-size: 14px;
}
h1, h2, h3 { margin: 0 0 8px; line-height: 1.25; }
h1 { font-size: 20px; } h2 { font-size: 16px; } h3 { font-size: 14px; }
button {
  background: var(--accent); color: #fff; border: 0; border-radius: 8px;
  padding: 8px 14px; font: inherit; font-weight: 600; cursor: pointer;
}
button:hover { background: var(--accent-strong); }
button.secondary { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); }
input, select {
  background: var(--surface-2); color: var(--text); border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 10px; font: inherit;
}
input[type="range"] { padding: 0; accent-color: var(--accent); width: 100%; }
label { font-size: 12px; color: var(--muted); display: block; margin-bottom: 4px; }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px; margin-bottom: 12px;
}
canvas, svg { max-width: 100%; display: block; }
`;

/**
 * The event bridge, injected into every sandbox.
 *
 * Generated code calls reportEvent(action, values) and the host relays it to
 * the Guide — so even a fully model-authored interactive feeds the guidance
 * loop. Also reports height, so the frame can size to its content.
 */
export const SANDBOX_BRIDGE = `
<script>
(function () {
  function post(msg) { try { parent.postMessage(Object.assign({ __synapse: true }, msg), "*"); } catch (e) {} }
  window.reportEvent = function (action, values) {
    post({ kind: "interaction", action: String(action || "interaction"), values: values || {} });
  };
  function height() {
    var b = document.body, e = document.documentElement;
    return Math.max(b.scrollHeight, b.offsetHeight, e.scrollHeight, e.offsetHeight);
  }
  var last = 0;
  function reportHeight() {
    var h = height();
    if (Math.abs(h - last) > 2) { last = h; post({ kind: "height", height: h }); }
  }
  window.addEventListener("load", reportHeight);
  new ResizeObserver(reportHeight).observe(document.documentElement);
  setInterval(reportHeight, 500);
  window.addEventListener("error", function (e) {
    post({ kind: "error", message: String((e && e.message) || "script error") });
  });
})();
<\/script>
`;

export const TIER_C_SYSTEM = `You are the Generator for Synapse, working at Tier C: you write a complete, self-contained interactive lab for a Malaysian Form 4-5 KSSM SPM science student (Physics, Chemistry, Biology).

You are here because no pre-built sim and no composed screen could express this experiment. So build the real thing.

# Output format
Return ONE self-contained HTML document and NOTHING else. No markdown fences, no commentary before
or after. Start at <!DOCTYPE html>.

# Hard constraints (your document is rejected if it breaks these)
- No network access of any kind. No <script src>, no <link href>, no fetch, no XHR, no CDN, no
  external fonts, no remote images. Everything inline. There is no network in the sandbox.
- No localStorage, sessionStorage, cookies, or indexedDB — the frame has an opaque origin and they
  throw.
- Plain vanilla JS. No React, no libraries, no build step, no imports.
- Draw with inline SVG or canvas. For images, draw them — do not link them.

# The design system is already injected
Do NOT write a <style> reset or pick your own colours. These CSS variables are already defined and
you should use them: --bg --surface --surface-2 --border --text --muted --accent --accent-strong
--success --warning --danger --radius. Styled already: body, h1-h3, button, button.secondary,
input, select, input[type=range], label, .card. Light and dark are both handled. Add only the
styles your specific interactive needs, and build them from those variables so you match the app.

# Report interactions (this is required)
The host is a teacher watching over the student's shoulder. Call the injected global whenever the
student does something meaningful:

    reportEvent("ran the simulation", { mass: 2.5, force: 10, result: "accelerated" });
    reportEvent("predicted: water moves left", { prediction: "left" });

Report predictions, runs, resets, and answers. Include the values that matter. Do not report every
slider tick — report the moments a teacher would want to respond to.

# What makes a good lab
- The student must PREDICT before they see the answer. Make them commit, then show them.
- Real science in real code. Integrate the equations of motion; do not fake an animation with a
  hardcoded outcome. If a value is derived, derive it.
- Make the effect BIG and visible. A demonstration that barely moves teaches nothing.
- Label everything with units. SPM students are marked on units.
- One idea per lab. Depth over breadth.
- It must work on first paint: sensible starting values, nothing blank until clicked.

# Accuracy
Every number, equation and constant must be correct and defensible for the KSSM SPM syllabus. A
student will trust this. Do not invent data. If you show a formula, show the one that drives your
code.`;

/**
 * Pull the HTML document out of the model's raw output.
 *
 * The prompt asks for a bare document, but models sometimes fence it anyway.
 * Cheaper to handle here than to spend a repair round-trip on it.
 */
export function extractHtml(raw: string): string {
  let text = raw.trim();

  const fence = text.match(/```(?:html)?\s*\n([\s\S]*?)```/);
  if (fence) text = fence[1].trim();

  const start = text.search(/<!DOCTYPE html>|<html[\s>]/i);
  if (start > 0) text = text.slice(start);

  return text.trim();
}

/**
 * Sanity-check a generated artifact before it reaches the screen.
 *
 * This is a guard against a model that ignored its instructions, not a security
 * boundary — the iframe sandbox is the security boundary. It catches the
 * failures that would render a dead lab (a CDN script that can never load) and
 * fails them into the fallback chain instead.
 */
export function validateGenerated(html: string): { ok: boolean; errors: string[] } {
  const errors: string[] = [];

  if (html.length < 200) errors.push("document is too short to be a real interactive");
  if (html.length > 400_000) errors.push("document is implausibly large");
  if (!/<html[\s>]/i.test(html)) errors.push("no <html> element");
  if (!/<script[\s>]/i.test(html)) errors.push("no <script> — this would not be interactive");

  // External references can never load inside the sandbox, so a document that
  // depends on one is already broken. Better to fall back than render a husk.
  const external = [
    [/<script[^>]+\bsrc\s*=/i, "<script src> (no network in the sandbox)"],
    [/<link[^>]+\bhref\s*=\s*["']https?:/i, "external stylesheet"],
    [/\bfetch\s*\(/i, "fetch()"],
    [/\bXMLHttpRequest\b/, "XMLHttpRequest"],
    [/\bimport\s*\(/, "dynamic import()"],
    [/<img[^>]+\bsrc\s*=\s*["']https?:/i, "remote image"],
    [/@import\s+url\(/i, "CSS @import"],
    [/\b(localStorage|sessionStorage|indexedDB)\b/, "storage API (throws on an opaque origin)"],
  ] as const;

  for (const [pattern, label] of external) {
    if (pattern.test(html)) errors.push(`uses ${label}`);
  }

  return { ok: errors.length === 0, errors };
}

/**
 * Assemble the final srcdoc: our CSP, our tokens, our bridge, their document.
 *
 * The CSP is defence in depth behind the sandbox attribute. default-src 'none'
 * with no connect-src means no egress even if the model smuggled a fetch past
 * validateGenerated.
 */
export function buildSrcdoc(html: string): string {
  const csp =
    "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; " +
    "script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:;\">";

  const injection = `${csp}\n<style>${SANDBOX_TOKENS}</style>`;

  // Prefer to inject inside the document's own <head> so our CSP and tokens
  // precede their content. Fall back to prepending if the head is unparseable.
  const headMatch = html.match(/<head[^>]*>/i);
  const withHead = headMatch
    ? html.replace(headMatch[0], `${headMatch[0]}\n${injection}`)
    : `${injection}\n${html}`;

  const bodyClose = withHead.lastIndexOf("</body>");
  return bodyClose === -1
    ? withHead + SANDBOX_BRIDGE
    : withHead.slice(0, bodyClose) + SANDBOX_BRIDGE + withHead.slice(bodyClose);
}
