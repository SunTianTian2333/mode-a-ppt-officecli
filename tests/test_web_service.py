from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest

from src.web.service import chat_sse, format_sse


def test_format_sse():
    frame = format_sse("tool_start", {"command": "officecli --version", "index": 1})
    assert frame.startswith("event: tool_start\n")
    assert '"command": "officecli --version"' in frame
    assert frame.endswith("\n\n")


@pytest.mark.asyncio
async def test_chat_sse_happy_path(monkeypatch):
    async def fake_stream(_message: str) -> AsyncIterator[dict[str, Any]]:
        yield {"type": "agent_turn", "turn": 1}
        yield {"type": "tool_start", "command": "officecli load_skill pptx", "index": 1, "slow": True}
        yield {"type": "tool_end", "summary": "44086 chars", "index": 1}
        yield {"type": "assistant", "text": "已生成 deck.pptx"}
        yield {"type": "complete", "final_state": {}, "tool_count": 1, "elapsed_s": 3.5}

    monkeypatch.setattr("src.web.service.run_ppt_agent_stream", fake_stream)
    monkeypatch.setattr("src.web.service.list_artifacts", lambda: [])

    frames = [frame async for frame in chat_sse("hello")]
    joined = "".join(frames)
    assert "event: agent_turn" in joined
    assert "event: tool_start" in joined
    assert "event: assistant" in joined
    assert "event: artifacts" in joined
    assert "event: done" in joined
    assert '"tool_count": 1' in joined


@pytest.mark.asyncio
async def test_chat_sse_runtime_error(monkeypatch):
    async def fake_stream(_message: str) -> AsyncIterator[dict[str, Any]]:
        raise RuntimeError("Agent 步数达到上限 (50)。")
        yield  # pragma: no cover

    monkeypatch.setattr("src.web.service.run_ppt_agent_stream", fake_stream)

    frames = [frame async for frame in chat_sse("hello")]
    assert any("event: error" in frame for frame in frames)
    assert not any("event: done" in frame for frame in frames)


@pytest.mark.asyncio
async def test_chat_sse_value_error(monkeypatch):
    async def fake_stream(_message: str) -> AsyncIterator[dict[str, Any]]:
        raise ValueError("OPENAI_API_KEY not set")
        yield  # pragma: no cover

    monkeypatch.setattr("src.web.service.run_ppt_agent_stream", fake_stream)

    frames = [frame async for frame in chat_sse("hello")]
    assert any("OPENAI_API_KEY not set" in frame for frame in frames)
