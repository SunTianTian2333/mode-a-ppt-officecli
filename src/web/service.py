"""Orchestrate a single chat run and format SSE frames."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from src.agent import run_ppt_agent_stream
from src.web.artifacts import list_artifacts


def format_sse(event_type: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {payload}\n\n"


async def chat_sse(message: str) -> AsyncIterator[str]:
    """Run one agent turn and yield SSE wire-format strings."""
    tool_count = 0
    elapsed_s = 0.0

    try:
        async for event in run_ppt_agent_stream(message):
            event_type = event["type"]
            if event_type == "agent_turn":
                yield format_sse("agent_turn", {"turn": event["turn"]})
            elif event_type == "tool_start":
                yield format_sse(
                    "tool_start",
                    {
                        "command": event["command"],
                        "index": event["index"],
                        "slow": event.get("slow", False),
                    },
                )
            elif event_type == "tool_end":
                yield format_sse(
                    "tool_end",
                    {"summary": event["summary"], "index": event["index"]},
                )
            elif event_type == "assistant":
                yield format_sse("assistant", {"text": event["text"]})
            elif event_type == "complete":
                tool_count = event["tool_count"]
                elapsed_s = event["elapsed_s"]
    except ValueError as exc:
        yield format_sse("error", {"message": str(exc)})
        return
    except RuntimeError as exc:
        yield format_sse("error", {"message": str(exc)})
        return

    files = list_artifacts()
    yield format_sse("artifacts", {"files": files})
    yield format_sse("done", {"elapsed_s": elapsed_s, "tool_count": tool_count})
