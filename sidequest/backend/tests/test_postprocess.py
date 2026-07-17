"""Unit tests for every post-processor rule (TECHNICAL.md section 4)."""

import postprocess as pp

ORIGIN = "http://localhost:3000"
MAX = 200_000

MINIMAL = (
    "<!doctype html>\n<html><head><title>t</title></head>"
    "<body><script>window.parent.postMessage({type:'axiom_ready'},'*');</script></body></html>"
)


def run(html: str):
    return pp.run(html, public_origin=ORIGIN, max_bytes=MAX)


# --- strip_markdown_fences ---


def test_strips_fences():
    fenced = f"```html\n{MINIMAL}\n```"
    assert pp.strip_markdown_fences(fenced) == MINIMAL


def test_leaves_unfenced_alone():
    assert pp.strip_markdown_fences(MINIMAL) == MINIMAL


# --- enforce_single_document ---


def test_prepends_missing_doctype():
    result = pp.enforce_single_document("<html><head></head><body></body></html>")
    assert isinstance(result, str) and result.lower().startswith("<!doctype html>")


def test_rejects_two_documents():
    result = pp.enforce_single_document(MINIMAL + "\n<html></html>")
    assert isinstance(result, pp.PostprocessReject)


# --- rewrite_external_scripts ---


def test_rewrites_known_cdn_to_vendor():
    html = MINIMAL.replace(
        "<body>",
        '<body><script src="https://cdn.jsdelivr.net/npm/p5@1.11.2/lib/p5.min.js"></script>',
    )
    result = pp.rewrite_external_scripts(html)
    assert isinstance(result, str)
    assert 'src="/vendor/p5.min.js"' in result
    assert "jsdelivr" not in result


def test_accepts_correct_vendor_path():
    html = MINIMAL.replace("<body>", '<body><script src="/vendor/d3.min.js"></script>')
    assert pp.rewrite_external_scripts(html) == html


def test_rejects_unknown_script_source():
    html = MINIMAL.replace("<body>", '<body><script src="https://evil.example/x.js"></script>')
    result = pp.rewrite_external_scripts(html)
    assert isinstance(result, pp.PostprocessReject)


def test_rewrites_katex_css_link():
    html = MINIMAL.replace(
        "</head>",
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"></head>',
    )
    result = pp.rewrite_external_scripts(html)
    assert isinstance(result, str) and 'href="/vendor/katex.min.css"' in result


# --- forbidden_api_scan (hostile inputs H1/H2 second layer) ---


def test_sanctioned_bridge_passes():
    assert pp.forbidden_api_scan(MINIMAL) == MINIMAL


def test_fetch_rejected():
    html = MINIMAL.replace("<body>", "<body><script>fetch('/x')</script>")
    result = pp.forbidden_api_scan(html)
    assert isinstance(result, pp.PostprocessReject)
    assert "fetch" in result.reason


def test_document_cookie_rejected():
    html = MINIMAL.replace("<body>", "<body><script>var c=document.cookie;</script>")
    assert isinstance(pp.forbidden_api_scan(html), pp.PostprocessReject)


def test_non_bridge_parent_access_rejected():
    html = MINIMAL.replace("<body>", "<body><script>window.parent.document.title='x'</script>")
    assert isinstance(pp.forbidden_api_scan(html), pp.PostprocessReject)


def test_absolute_url_rejected():
    html = MINIMAL.replace("<body>", "<body><img src='https://example.com/x.png'>")
    assert isinstance(pp.forbidden_api_scan(html), pp.PostprocessReject)


def test_localstorage_rejected():
    html = MINIMAL.replace("<body>", "<body><script>localStorage.setItem('a','b')</script>")
    assert isinstance(pp.forbidden_api_scan(html), pp.PostprocessReject)


def test_eval_and_new_function_rejected():
    for snippet in ("eval('1')", "new Function('return 1')"):
        html = MINIMAL.replace("<body>", f"<body><script>{snippet}</script>")
        assert isinstance(pp.forbidden_api_scan(html), pp.PostprocessReject), snippet


# --- injections ---


def test_viewport_injected_once():
    result = pp.ensure_viewport(MINIMAL)
    assert isinstance(result, str) and 'name="viewport"' in result
    assert pp.ensure_viewport(result) == result


def test_charset_injected():
    result = pp.ensure_charset(MINIMAL)
    assert isinstance(result, str) and 'charset="utf-8"' in result


def test_error_banner_injected_once():
    result = pp.inject_error_banner(MINIMAL)
    assert isinstance(result, str) and "axiom-error-banner" in result
    assert pp.inject_error_banner(result) == result


def test_csp_injected_and_authoritative():
    model_csp = MINIMAL.replace(
        "<head>", '<head><meta http-equiv="Content-Security-Policy" content="default-src *">'
    )
    result = pp.make_inject_csp(ORIGIN)(model_csp)
    assert isinstance(result, str)
    assert result.count("Content-Security-Policy") == 1
    assert "default-src 'none'" in result
    assert f"script-src 'unsafe-inline' {ORIGIN}" in result


def test_csp_lands_before_scripts_in_full_run():
    html = MINIMAL.replace("</head>", '<script src="/vendor/p5.min.js"></script></head>')
    result = run(html)
    assert isinstance(result, str)
    assert result.index("Content-Security-Policy") < result.index("/vendor/p5.min.js")


# --- size cap ---


def test_size_cap_rejects_oversized():
    big = MINIMAL.replace("<body>", "<body>" + "x" * MAX)
    result = pp.make_size_cap(MAX)(big)
    assert isinstance(result, pp.PostprocessReject)


# --- full chain ---


def test_full_chain_happy_path():
    fenced = f"```html\n{MINIMAL}\n```"
    result = run(fenced)
    assert isinstance(result, str)
    for needle in ("viewport", "charset", "axiom-error-banner", "Content-Security-Policy"):
        assert needle in result


def test_full_chain_rejects_hostile_fetch():
    hostile = MINIMAL.replace("<body>", "<body><script>fetch('https://example.com/log')</script>")
    result = run(hostile)
    assert isinstance(result, pp.PostprocessReject)
    assert result.rule == "forbidden_api_scan"
