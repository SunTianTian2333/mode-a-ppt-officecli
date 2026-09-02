from __future__ import annotations

from typing import Any

import pytest
from langgraph.errors import GraphRecursionError

from src.agent_runtime import AgentRunOptions, stream_agent


class _FakeAgent:
    def __init__(self, events: list[dict[str, Any]], *, captured: list | None = None) -> None:
        self._events = events
        self._captured = captured

    async def astream_events(
        self,
        input_payload: object,
        *,
        version: str = "v2",
        config: dict | None = None,
    ):
        if self._captured is not None:
            self._captured.append({"payload": input_payload, "config": config})
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


@pytest.mark.asyncio
async def test_stream_agent_accepts_message_list():
    captured: list = []
    events = [
        {
            "event": "on_chain_end",
            "data": {"output": {"messages": ["history"]}},
        },
    ]
    history = ["m1", "m2"]
    state = await stream_agent(
        _FakeAgent(events, captured=captured),
        history,
        options=AgentRunOptions(quiet=True),
    )
    assert captured == [{"payload": {"messages": history}, "config": {"recursion_limit": 9999}}]
    assert state == {"messages": ["history"]}


@pytest.mark.asyncio
async def test_stream_agent_passes_recursion_limit(monkeypatch):
    monkeypatch.setenv("PPT_RECURSION_LIMIT", "120")
    captured: list = []
    events = [
        {
            "event": "on_chain_end",
            "data": {"output": {"messages": ["done"]}},
        },
    ]
    await stream_agent(
        _FakeAgent(events, captured=captured),
        "hello",
        options=AgentRunOptions(quiet=True),
    )
    assert captured[0]["config"] == {"recursion_limit": 120}


@pytest.mark.asyncio
async def test_stream_agent_recursion_limit_error(monkeypatch):
    monkeypatch.setenv("PPT_RECURSION_LIMIT", "50")

    class _LimitAgent:
        async def astream_events(self, input_payload, *, version="v2", config=None):
            raise GraphRecursionError("limit reached")
            yield  # pragma: no cover

    with pytest.raises(RuntimeError, match="Agent 步数达到上限 \\(50\\)"):
        await stream_agent(_LimitAgent(), "hello", options=AgentRunOptions(quiet=True))


@pytest.mark.asyncio
async def test_iter_agent_events_yields_normalized_events():
    events = [
        {"event": "on_chat_model_start", "data": {}},
        {
            "event": "on_tool_start",
            "data": {"input": {"command": "officecli load_skill pptx"}},
        },
        {"event": "on_tool_end", "data": {"output": "ok"}},
        {
            "event": "on_chain_end",
            "data": {"output": {"messages": ["done"]}},
        },
    ]

    from src.agent_runtime import iter_agent_events

    collected = [ev async for ev in iter_agent_events(_FakeAgent(events), "hello")]
    kinds = [ev["type"] for ev in collected]
    assert kinds == ["agent_turn", "tool_start", "tool_end", "complete"]
    assert collected[-1]["final_state"] == {"messages": ["done"]}
