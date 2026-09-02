from __future__ import annotations

from typing import Any

import pytest

from src.agent_runtime import AgentRunOptions, stream_agent


class _FakeAgent:
    def __init__(self, events: list[dict[str, Any]]) -> None:
        self._events = events

    async def astream_events(self, _input: object, *, version: str = "v2"):
        for event in self._events:
            yield event


@pytest.mark.asyncio
async def test_stream_agent_prints_progress(capsys):
    events = [
        {"event": "on_chat_model_start", "data": {}},
        {
            "event": "on_tool_start",
            "data": {"input": {"command": "officecli load_skill pptx"}},
        },
        {"event": "on_tool_end", "data": {"output": "x" * 600}},
        {
            "event": "on_chain_end",
            "data": {"output": {"messages": ["done"]}},
        },
    ]
    state = await stream_agent(_FakeAgent(events), "hello", options=AgentRunOptions())
    out = capsys.readouterr().out
    assert "[agent] turn 1" in out
    assert "[tool] officecli load_skill pptx" in out
    assert "600 chars" in out
    assert "[agent] done · 1 tools" in out
    assert state == {"messages": ["done"]}


@pytest.mark.asyncio
async def test_stream_agent_quiet(capsys):
    events = [
        {"event": "on_chat_model_start", "data": {}},
        {
            "event": "on_chain_end",
            "data": {"output": {"messages": ["done"]}},
        },
    ]
    await stream_agent(_FakeAgent(events), "hello", options=AgentRunOptions(quiet=True))
    out = capsys.readouterr().out
    assert out == ""
