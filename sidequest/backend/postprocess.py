"""Deterministic output fixes and safety scans for Generator output.

Each rule is a pure function `str -> str | PostprocessReject` with a unit test
and a comment citing the failure class it fixes (TECHNICAL.md section 4). Per
CLAUDE.md, a Generator failure class seen 3+ times becomes a rule here instead
of a prompt addition; this file is expected to grow.

Rule order matters and is load-bearing:
- vendor rewrite runs BEFORE the forbidden-API scan, so known CDN URLs are
  normalized to /vendor/ paths instead of tripping the absolute-URL check;
- the forbidden-API scan runs BEFORE CSP/banner injection, so the scan never
  sees the origin literal and sanctioned postMessage lines we inject ourselves
  (SECURITY.md section 2.3 ordering rule).

A scan hit is a reject (counts as a verifier fail for retry purposes), never
an auto-strip: auto-stripping produces silently broken artifacts
(SECURITY.md section 3).
"""

import re
from dataclasses import dataclass


@dataclass
class PostprocessReject:
    rule: str
    reason: str


# --- vendored library canon ---------------------------------------------------

# filename variants the model plausibly emits -> the canonical vendored file
VENDOR_CANON: dict[str, str] = {
    "p5.min.js": "p5.min.js",
    "p5.js": "p5.min.js",
    "matter.min.js": "matter.min.js",
    "matter.js": "matter.min.js",
    "three.min.js": "three.min.js",
    "three.js": "three.min.js",
    "chart.min.js": "chart.min.js",
    "chart.umd.js": "chart.min.js",
    "chart.js": "chart.min.js",
    "d3.min.js": "d3.min.js",
    "d3.v7.min.js": "d3.min.js",
    "d3.js": "d3.min.js",
    "katex.min.js": "katex.min.js",
    "katex.js": "katex.min.js",
}
VENDOR_CSS_CANON: dict[str, str] = {
    "katex.min.css": "katex.min.css",
    "katex.css": "katex.min.css",
}


# --- rules --------------------------------------------------------------------


def strip_markdown_fences(html: str) -> str | PostprocessReject:
    """Fixes: model wraps the document in ```html fences despite instructions."""
    text = html.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
    return text.strip()


def enforce_single_document(html: str) -> str | PostprocessReject:
    """Fixes: missing doctype (prepend). Rejects: multiple <html> documents,
    which happens when the model emits an explanation plus a second attempt."""
    if len(re.findall(r"<html\b", html, flags=re.IGNORECASE)) > 1:
        return PostprocessReject("enforce_single_document", "more than one <html> element")
    if not re.match(r"\s*<!doctype\s+html", html, flags=re.IGNORECASE):
        html = "<!doctype html>\n" + html
    return html


def rewrite_external_scripts(html: str) -> str | PostprocessReject:
    """Fixes: model cites a CDN URL for a known library despite instructions;
    rewrite to the vendored path. Rejects: any script/stylesheet source we do
    not vendor (no runtime CDN, hard rule 3 in CLAUDE.md)."""
    reject: PostprocessReject | None = None

    def fix_src(match: re.Match) -> str:
        nonlocal reject
        url = match.group("url")
        basename = url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
        if url.startswith("/vendor/") and basename in VENDOR_CANON.values():
            return match.group(0)
        if basename in VENDOR_CANON:
            return match.group(0).replace(url, f"/vendor/{VENDOR_CANON[basename]}")
        reject = reject or PostprocessReject(
            "rewrite_external_scripts", f"non-vendored script source: {url}"
        )
        return match.group(0)

    def fix_href(match: re.Match) -> str:
        nonlocal reject
        url = match.group("url")
        basename = url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
        if url.startswith("/vendor/") and basename in VENDOR_CSS_CANON.values():
            return match.group(0)
        if basename in VENDOR_CSS_CANON:
            return match.group(0).replace(url, f"/vendor/{VENDOR_CSS_CANON[basename]}")
        reject = reject or PostprocessReject(
            "rewrite_external_scripts", f"non-vendored stylesheet: {url}"
        )
        return match.group(0)

    html = re.sub(
        r"<script\b[^>]*\bsrc\s*=\s*[\"'](?P<url>[^\"']+)[\"'][^>]*>",
        fix_src,
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<link\b[^>]*\bhref\s*=\s*[\"'](?P<url>[^\"']+)[\"'][^>]*>",
        fix_href,
        html,
        flags=re.IGNORECASE,
    )
    return reject or html


# Sanctioned bridge call; removed from the text before scanning so any OTHER
# window.parent / window.top use is caught (SECURITY.md section 3).
_SANCTIONED_BRIDGE = re.compile(r"window\.parent\.postMessage\s*\(")

# (pattern, human label). Deterministic second layer; the Verifier is the
# semantic first layer that also catches obfuscation.
FORBIDDEN_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bfetch\s*\("), "fetch"),
    (re.compile(r"\bXMLHttpRequest\b"), "XMLHttpRequest"),
    (re.compile(r"\bWebSocket\b"), "WebSocket"),
    (re.compile(r"\bEventSource\b"), "EventSource"),
    (re.compile(r"\bsendBeacon\b"), "navigator.sendBeacon"),
    (re.compile(r"\bimportScripts\b"), "importScripts"),
    (re.compile(r"\bimport\s*\("), "dynamic import()"),
    (re.compile(r"^\s*import\s+", re.MULTILINE), "ES module import"),
    (re.compile(r"^\s*export\s+", re.MULTILINE), "ES module export"),
    (re.compile(r"\beval\s*\("), "eval"),
    (re.compile(r"\bnew\s+Function\b"), "new Function"),
    (re.compile(r"document\s*\.\s*cookie"), "document.cookie"),
    (re.compile(r"\blocalStorage\b"), "localStorage"),
    (re.compile(r"\bsessionStorage\b"), "sessionStorage"),
    (re.compile(r"\bindexedDB\b"), "indexedDB"),
    (re.compile(r"window\s*\.\s*open\s*\("), "window.open"),
    (re.compile(r"window\s*\.\s*parent\b"), "window.parent (non-bridge)"),
    (re.compile(r"window\s*\.\s*top\b"), "window.top"),
    (re.compile(r"location\s*\.\s*(assign|replace)\s*\("), "location navigation"),
    (re.compile(r"location\s*\.\s*href\s*="), "location.href write"),
    (re.compile(r"\bNotification\b"), "Notification"),
    (re.compile(r"\bgeolocation\b"), "geolocation"),
    (re.compile(r"\bgetUserMedia\b"), "getUserMedia"),
    (re.compile(r"\bserviceWorker\b"), "serviceWorker"),
    (re.compile(r"\bSharedWorker\b"), "SharedWorker"),
    (re.compile(r"\bnew\s+Worker\s*\("), "Worker"),
    (re.compile(r"https?://", re.IGNORECASE), "absolute URL"),
    (re.compile(r"(?:src|href)\s*=\s*[\"']//"), "protocol-relative URL"),
    (re.compile(r"url\(\s*[\"']?//"), "protocol-relative URL in CSS"),
]


def forbidden_api_scan(html: str) -> str | PostprocessReject:
    """Deterministic deny-list scan (SECURITY.md section 3). Second, independent
    layer behind the Verifier. A hit rejects the artifact outright."""
    scannable = _SANCTIONED_BRIDGE.sub("__AXIOM_BRIDGE__(", html)
    hits = [label for pattern, label in FORBIDDEN_PATTERNS if pattern.search(scannable)]
    if hits:
        return PostprocessReject("forbidden_api_scan", "forbidden API(s): " + ", ".join(hits))
    return html


def ensure_viewport(html: str) -> str | PostprocessReject:
    """Fixes: missing viewport meta breaks the 360px mobile requirement."""
    if re.search(r"<meta\b[^>]*name\s*=\s*[\"']viewport[\"']", html, flags=re.IGNORECASE):
        return html
    tag = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    return _inject_into_head(html, tag)


def ensure_charset(html: str) -> str | PostprocessReject:
    """Fixes: missing charset garbles degree signs and greek letters."""
    if re.search(r"<meta\b[^>]*charset", html, flags=re.IGNORECASE):
        return html
    return _inject_into_head(html, '<meta charset="utf-8">')


ERROR_BANNER_SNIPPET = (
    "<script>(function(){window.addEventListener('error',function(e){"
    "var b=document.getElementById('axiom-error-banner');"
    "if(!b){b=document.createElement('div');b.id='axiom-error-banner';"
    "b.style.cssText='position:fixed;left:0;right:0;bottom:0;padding:8px 12px;"
    "background:#7f1d1d;color:#fecaca;font:13px system-ui;z-index:9999';"
    "document.body&&document.body.appendChild(b);}"
    "b.textContent='This simulation hit an error: '+(e.message||'unknown');"
    "try{window.parent.postMessage({type:'axiom_error',"
    "message:String(e.message||'unknown').slice(0,512)},'*');}catch(_){}"
    "});})();</script>"
)


def inject_error_banner(html: str) -> str | PostprocessReject:
    """Wraps uncaught errors: visible in-artifact banner plus axiom_error to the
    bridge, so failures degrade the card instead of silently freezing."""
    if "axiom-error-banner" in html:
        return html
    return _inject_into_head(html, ERROR_BANNER_SNIPPET)


def make_inject_csp(public_origin: str):
    csp = (
        "default-src 'none'; "
        f"script-src 'unsafe-inline' {public_origin}; "
        f"style-src 'unsafe-inline' {public_origin}; "
        "img-src data:; "
        f"font-src {public_origin} data:; "
        "connect-src 'none'; frame-src 'none'; object-src 'none'; "
        "base-uri 'none'; form-action 'none';"
    )
    tag = f'<meta http-equiv="Content-Security-Policy" content="{csp}">'

    def inject_csp(html: str) -> str | PostprocessReject:
        """Injects the artifact CSP (SECURITY.md section 2.3). Any CSP meta the
        model wrote itself is removed first; ours is authoritative."""
        html = re.sub(
            r"<meta\b[^>]*http-equiv\s*=\s*[\"']Content-Security-Policy[\"'][^>]*>\s*",
            "",
            html,
            flags=re.IGNORECASE,
        )
        # Injected last in the rule chain, and _inject_into_head prepends, so
        # the CSP lands first in <head>, ahead of every script it governs.
        return _inject_into_head(html, tag)

    return inject_csp


def make_size_cap(max_bytes: int):
    def size_cap(html: str) -> str | PostprocessReject:
        """Rejects oversized artifacts (TECHNICAL.md performance budgets)."""
        size = len(html.encode("utf-8"))
        if size > max_bytes:
            return PostprocessReject("size_cap", f"artifact is {size} bytes (max {max_bytes})")
        return html

    return size_cap


def _inject_into_head(html: str, tag: str) -> str:
    match = re.search(r"<head\b[^>]*>", html, flags=re.IGNORECASE)
    if match:
        return html[: match.end()] + "\n" + tag + html[match.end() :]
    # No <head>: fall back to right after <html>, or prepend.
    match = re.search(r"<html\b[^>]*>", html, flags=re.IGNORECASE)
    if match:
        return html[: match.end()] + "\n<head>" + tag + "</head>" + html[match.end() :]
    return tag + "\n" + html


def build_rules(*, public_origin: str, max_bytes: int) -> list:
    """The ordered v1 chain. See module docstring for why the order matters."""
    return [
        strip_markdown_fences,
        enforce_single_document,
        rewrite_external_scripts,
        forbidden_api_scan,
        ensure_viewport,
        ensure_charset,
        inject_error_banner,
        make_inject_csp(public_origin),
        make_size_cap(max_bytes),
    ]


def run(html: str, *, public_origin: str, max_bytes: int) -> str | PostprocessReject:
    for rule in build_rules(public_origin=public_origin, max_bytes=max_bytes):
        result = rule(html)
        if isinstance(result, PostprocessReject):
            return result
        html = result
    return html
