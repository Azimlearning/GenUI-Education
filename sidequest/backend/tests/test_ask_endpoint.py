"""End-to-end SSE test of POST /api/ask in echo mode (no LLM, no DB)."""

import json

import httpx
import pytest

import api.ask as ask_module
import graph.nodes.explainer as explainer_module
import graph.nodes.router as router_module
from main import app


async def _noop(*args, **kwargs):
    return None


@pytest.fixture(autouse=True)
def no_db(monkeypatch):
    monkeypatch.setattr(ask_module, "ensure_session", _noop)
    monkeypatch.setattr(ask_module, "save_message", _noop)
    monkeypatch.setattr(router_module, "record_trace", _noop)
    monkeypatch.setattr(explainer_module, "record_trace", _noop)


def parse_frames(raw: str) -> list[tuple[int, str, dict]]:
    frames = []
    for block in raw.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.split("\n"))
        frames.append((int(lines["id"]), lines["event"], json.loads(lines["data"])))
    return frames


async def ask(message: str = "why does ice float?") -> list[tuple[int, str, dict]]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/ask", json={"session_id": "test-session-1", "message": message}
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        return parse_frames(resp.text)


async def test_stream_order_and_shapes():
    frames = await ask()
    names = [name for _, name, _ in frames]

    assert names[0] == "meta"
    assert names[-1] == "done"
    assert "text_delta" in names
    assert names.index("text_done") < names.index("done")

    ids = [event_id for event_id, _, _ in frames]
    assert ids == sorted(ids) and len(set(ids)) == len(ids)

    meta = frames[0][2]
    assert meta["cache"] == "miss"
    assert meta["intent"]["artifact_type"] == "text_only"  # echo mode routes text_only

    text = "".join(d["chunk"] for _, name, d in frames if name == "text_delta")
    assert "why does ice float?" in text

    done = frames[-1][2]
    assert set(done) == {"usage", "timings_ms"}


async def test_oversized_query_rejected_without_llm_spend():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/ask", json={"session_id": "test-session-1", "message": "x" * 5000}
        )
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["retryable"] is False


async def test_short_session_id_rejected():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/ask", json={"session_id": "abc", "message": "hi"})
    assert resp.status_code == 422
