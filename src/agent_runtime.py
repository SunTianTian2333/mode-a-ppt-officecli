"""Agent runtime: stream events to terminal and return final state."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

_SLOW_TOOL_MARKERS = ("load_skill", "screenshot", "validate")

AgentMessages = str | list[Any]


@dataclass
class AgentRunOptions:
    verbose: bool = False
    quiet: bool = False


def truncate_text(text: str, limit: int = 200) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}…"


def format_tool_command(tool_input: object) -> str:
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
        return str(tool_input)
    return str(tool_input)


def format_tool_output(output: object, *, verbose: bool) -> str:
    text = _output_to_text(output)
    if not text:
        return "ok"
    if not verbose and len(text) > 500:
        return f"{len(text)} chars"
    if verbose and len(text) > 2000:
        return f"{text[:2000]}… ({len(text)} chars)"
    if not verbose:
        return truncate_text(text, 200)
    return text


def _output_to_text(output: object) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        if "command" in output:
            return str(output.get("command", ""))
        return str(output)
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(output)


def _log(line: str, *, quiet: bool) -> None:
    if not quiet:
        print(line, flush=True)


def _slow_hint(command: str) -> str:
    lowered = command.lower()
    if any(marker in lowered for marker in _SLOW_TOOL_MARKERS):
        return " (may take a while)"
    return ""


async def stream_agent(
    agent: Any,
    messages: AgentMessages,
    *,
    options: AgentRunOptions | None = None,
) -> dict[str, Any]:
    """Run agent with progress logs; return final graph state.

    ``messages`` may be a single user string (one-shot CLI) or a full message list (REPL).
    """
    opts = options or AgentRunOptions()
    if opts.verbose and opts.quiet:
        raise ValueError("cannot use --verbose and --quiet together")

    started = time.monotonic()
    turn = 0
    tool_count = 0
    final_state: dict[str, Any] | None = None
    payload = {"messages": messages}

    async for event in agent.astream_events(
        payload,
        version="v2",
    ):
        kind = event.get("event")
        data = event.get("data") or {}

        if kind == "on_chat_model_start":
            turn += 1
            _log(f"[agent] turn {turn} · LLM…", quiet=opts.quiet)

        elif kind == "on_tool_start":
            tool_input = data.get("input")
            command = format_tool_command(tool_input)
            tool_count += 1
            if opts.verbose:
                _log(f"[tool] {command}{_slow_hint(command)}", quiet=opts.quiet)
            else:
                _log(
                    f"[tool] {truncate_text(command, 120)}{_slow_hint(command)}",
                    quiet=opts.quiet,
                )

        elif kind == "on_tool_end":
            if opts.quiet:
                continue
            tool_output = data.get("output")
            summary = format_tool_output(tool_output, verbose=opts.verbose)
            prefix = "  → " if not opts.verbose else "  → output: "
            _log(f"{prefix}{summary}", quiet=False)

        elif kind == "on_chain_end":
            output = data.get("output")
            if isinstance(output, dict) and "messages" in output:
                final_state = output

    elapsed = time.monotonic() - started
    _log(
        f"[agent] done · {tool_count} tools · {elapsed:.1f}s",
        quiet=opts.quiet,
    )

    if final_state is None:
        raise RuntimeError("agent finished without messages in final state")
    return final_state
