from __future__ import annotations

from src.agent_runtime import (
    format_tool_command,
    format_tool_output,
    truncate_text,
)


def test_truncate_text():
    assert truncate_text("hello world", 20) == "hello world"
    assert truncate_text("x" * 30, 20) == f"{'x' * 20}…"


def test_format_tool_command():
    assert format_tool_command({"command": "officecli --version"}) == "officecli --version"


def test_format_tool_output_load_skill_default():
    text = "x" * 1000
    assert format_tool_output(text, verbose=False) == "1000 chars"


def test_format_tool_output_verbose_short():
    assert format_tool_output("Created deck", verbose=True) == "Created deck"
