from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.repl import parse_repl_command, run_ppt_chat


def test_parse_repl_command():
    assert parse_repl_command("/exit") == "exit"
    assert parse_repl_command("/quit") == "exit"
    assert parse_repl_command("/new") == "new"
    assert parse_repl_command("/help") == "help"
    assert parse_repl_command("做 PPT") is None


@pytest.mark.asyncio
async def test_run_ppt_chat_two_rounds(monkeypatch):
    inputs = iter(["第一轮", "第二轮", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calls: list[Any] = []

    async def fake_stream(_agent, messages, *, options=None):
        calls.append(list(messages))
        if len(calls) == 1:
            return {
                "messages": messages
                + [AIMessage(content="deck created at output/a.pptx")]
            }
        return {
            "messages": messages + [AIMessage(content="title updated on slide 2")]
        }

    monkeypatch.setattr("src.repl.stream_agent", fake_stream)
    monkeypatch.setattr("src.repl.officecli_tools_session", _fake_session)
    monkeypatch.setattr("src.repl.build_agent", lambda tools, **kw: object())
    monkeypatch.setattr("src.repl.build_system_prompt", lambda: "system")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    code = await run_ppt_chat()
    assert code == 0
    assert len(calls) == 2
    assert isinstance(calls[0][0], HumanMessage)
    assert calls[0][0].content == "第一轮"
    assert len(calls[1]) == 3
    assert calls[1][0].content == "第一轮"
    assert calls[1][1].content == "deck created at output/a.pptx"
    assert calls[1][2].content == "第二轮"


@pytest.mark.asyncio
async def test_run_ppt_chat_runtime_error_continues(monkeypatch, capsys):
    inputs = iter(["会失败", "继续", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    calls: list[Any] = []

    async def fake_stream(_agent, messages, *, options=None):
        calls.append(list(messages))
        if len(calls) == 1:
            raise RuntimeError("Agent 步数达到上限 (50)。")
        return {
            "messages": messages + [AIMessage(content="ok after error")]
        }

    monkeypatch.setattr("src.repl.stream_agent", fake_stream)
    monkeypatch.setattr("src.repl.officecli_tools_session", _fake_session)
    monkeypatch.setattr("src.repl.build_agent", lambda tools, **kw: object())
    monkeypatch.setattr("src.repl.build_system_prompt", lambda: "system")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    code = await run_ppt_chat(quiet=True)
    out = capsys.readouterr().out

    assert code == 0
    assert len(calls) == 2
    assert "[chat] error: Agent 步数达到上限 (50)。" in out
    assert "Assistant> ok after error" in out
    assert len(calls[1]) == 1
    assert calls[1][0].content == "继续"


class _fake_session:
    async def __aenter__(self):
        return [object()]

    async def __aexit__(self, *args):
        return False
