"""OfficeCLI MCP Client — LangChain Agent 作为 MCP Client 连接 officecli mcp."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TypeVar

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from src.config import officecli_mcp_connection

OFFICECLI_TOOL_NAME = "officecli"
OFFICECLI_SERVER = "officecli"

T = TypeVar("T")


def connection_config() -> dict[str, dict[str, object]]:
    return officecli_mcp_connection()


def make_mcp_client(*, handle_tool_errors: bool = True) -> MultiServerMCPClient:
    return MultiServerMCPClient(
        connection_config(),
        handle_tool_errors=handle_tool_errors,
    )


@asynccontextmanager
async def officecli_tools_session(
    *, handle_tool_errors: bool = True
) -> AsyncIterator[list[BaseTool]]:
    """Long-lived MCP session: all tool calls share one officecli mcp subprocess."""
    client = make_mcp_client(handle_tool_errors=handle_tool_errors)
    async with client.session(OFFICECLI_SERVER) as session:
        tools = await load_mcp_tools(session)
        yield tools


async def run_with_officecli_tools(
    fn: Callable[[list[BaseTool]], Awaitable[T]],
    *,
    handle_tool_errors: bool = True,
) -> T:
    async with officecli_tools_session(handle_tool_errors=handle_tool_errors) as tools:
        return await fn(tools)


def _tool_result_to_text(result: object) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        parts: list[str] = []
        for item in result:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(result)


def _find_officecli_tool(tools: list[BaseTool]) -> BaseTool:
    for tool in tools:
        if tool.name == OFFICECLI_TOOL_NAME or tool.name.endswith(
            f"_{OFFICECLI_TOOL_NAME}"
        ):
            return tool
    names = [t.name for t in tools]
    raise RuntimeError(f"officecli tool not found in MCP tools: {names}")


async def get_officecli_tools(*, handle_tool_errors: bool = True) -> list[BaseTool]:
    """Short tasks: each tool call spawns a new MCP session (adapter default)."""
    client = make_mcp_client(handle_tool_errors=handle_tool_errors)
    return await client.get_tools()


async def call_officecli(command: str, *, tools: list[BaseTool] | None = None) -> str:
    """Run officecli via MCP.

    Reuses the session when ``tools`` come from ``officecli_tools_session``;
    otherwise each call may spawn a new ``officecli mcp`` subprocess.
    """
    owned_tools = tools
    if owned_tools is None:
        owned_tools = await get_officecli_tools()
    tool = _find_officecli_tool(owned_tools)
    raw = await tool.ainvoke({"command": command})
    return _tool_result_to_text(raw)
