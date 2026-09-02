from __future__ import annotations

from pathlib import Path

import pytest

from src.config import ensure_output_dir
from src.mcp_client import (
    OFFICECLI_TOOL_NAME,
    call_officecli,
    get_officecli_tools,
    officecli_tools_session,
)


@pytest.mark.asyncio
async def test_get_tools_returns_officecli():
    tools = await get_officecli_tools()
    names = [t.name for t in tools]
    assert any(
        n == OFFICECLI_TOOL_NAME or n.endswith(f"_{OFFICECLI_TOOL_NAME}") for n in names
    )


@pytest.mark.asyncio
async def test_call_version():
    tools = await get_officecli_tools()
    text = await call_officecli("officecli --version", tools=tools)
    assert "1.0" in text


@pytest.mark.asyncio
async def test_call_create_pptx():
    output_dir = ensure_output_dir()
    pptx_path = output_dir / "step2-test.pptx"
    pptx_path.unlink(missing_ok=True)

    tools = await get_officecli_tools()
    cmd = f"officecli create {pptx_path.resolve()}"
    text = await call_officecli(cmd, tools=tools)

    assert pptx_path.is_file()
    assert pptx_path.stat().st_size > 0
    assert "Created" in text or pptx_path.suffix == ".pptx"


@pytest.mark.asyncio
async def test_session_bound_tools_multiple_calls():
    async with officecli_tools_session() as tools:
        first = await call_officecli("officecli --version", tools=tools)
        second = await call_officecli("officecli --version", tools=tools)
    assert "1.0" in first
    assert "1.0" in second
