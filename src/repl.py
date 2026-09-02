"""Interactive REPL for multi-turn PPT editing."""

from __future__ import annotations

import asyncio
from typing import Literal

from langchain_core.messages import HumanMessage

from src.agent import build_agent, extract_final_text
from src.agent_runtime import AgentRunOptions, stream_agent
from src.config import get_openai_settings, load_config
from src.mcp_client import officecli_tools_session
from src.prompts.loader import build_system_prompt

ReplCommand = Literal["exit", "new", "help"]


def parse_repl_command(line: str) -> ReplCommand | None:
    normalized = line.strip().lower()
    if normalized in ("/exit", "/quit", "exit", "quit"):
        return "exit"
    if normalized == "/new":
        return "new"
    if normalized == "/help":
        return "help"
    return None


def print_repl_help() -> None:
    print(
        "\n".join(
            [
                "Commands:",
                "  /help   — this message",
                "  /new    — clear chat history (new deck task)",
                "  /exit   — quit (Ctrl+D also exits)",
                "",
                "Examples:",
                '  做一个 LangChain 教学 PPT',
                '  把第 2 页标题改成「学习路线」',
            ]
        )
    )


async def run_ppt_chat(*, verbose: bool = False, quiet: bool = False) -> int:
    """Multi-turn chat; one MCP session for the whole REPL."""
    load_config()
    settings = get_openai_settings()
    if not settings["api_key"]:
        raise ValueError("OPENAI_API_KEY not set")
    if verbose and quiet:
        raise ValueError("cannot use --verbose and --quiet together")

    system = build_system_prompt()
    options = AgentRunOptions(verbose=verbose, quiet=quiet)

    if not quiet:
        print("mode-a-ppt-officecli · chat")
        print("MCP session ready. Type /help for commands.\n")

    async with officecli_tools_session() as tools:
        agent = build_agent(tools, system_prompt=system)
        messages: list = []

        while True:
            try:
                line = await asyncio.to_thread(input, "PPT> ")
            except EOFError:
                break

            line = line.strip()
            if not line:
                continue

            command = parse_repl_command(line)
            if command == "exit":
                break
            if command == "new":
                messages = []
                print("[chat] history cleared\n")
                continue
            if command == "help":
                print_repl_help()
                print()
                continue

            messages.append(HumanMessage(content=line))
            try:
                state = await stream_agent(agent, messages, options=options)
            except KeyboardInterrupt:
                if messages and isinstance(messages[-1], HumanMessage):
                    messages.pop()
                print("\n[chat] round cancelled\n")
                continue

            messages = list(state["messages"])
            reply = extract_final_text(state)
            print(f"\nAssistant> {reply}\n")

    if not quiet:
        print("bye.")
    return 0
