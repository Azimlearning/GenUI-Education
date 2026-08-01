from graph.nodes.generator import extract_complete_html


def test_extract_complete_html_removes_a_markdown_fence():
    raw = "```html\n<!doctype html><html><body>Lab</body></html>\n```"
    assert extract_complete_html(raw) == "<!doctype html><html><body>Lab</body></html>"


def test_extract_complete_html_rejects_a_truncated_document():
    assert extract_complete_html("<!doctype html><html><body>Lab") is None
