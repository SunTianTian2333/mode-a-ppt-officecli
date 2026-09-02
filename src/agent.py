"""Agent assembly (Step 4): create_agent + MCP tools in a long-lived session."""

from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from src.agent_runtime import AgentRunOptions, stream_agent
from src.config import get_openai_settings, load_config
from src.mcp_client import officecli_tools_session
from src.prompts.loader import build_system_prompt


def build_agent(tools: list[BaseTool], *, system_prompt: str | None = None):
    """Create LangChain agent bound to session-scoped MCP tools."""
    settings = get_openai_settings()
    if not settings["api_key"]:
        raise ValueError("OPENAI_API_KEY not set")

    llm = ChatOpenAI(
        api_key=settings["api_key"],
        base_url=settings["base_url"],
        model=settings["model"],
    )
    prompt = system_prompt if system_prompt is not None else build_system_prompt()
    return create_agent(llm, tools, system_prompt=prompt)


def extract_final_text(result: object) -> str:
    if isinstance(result, dict):
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                return str(msg.content)
    return str(result)


async def run_ppt_agent(
    user_message: str,
    *,
    verbose: bool = False,
    quiet: bool = False,
) -> str:
    """Run one PPT task; MCP session lives for the entire agent loop."""
    load_config()
    settings = get_openai_settings()
    if not settings["api_key"]:
        raise ValueError("OPENAI_API_KEY not set")
    if verbose and quiet:
        raise ValueError("cannot use --verbose and --quiet together")

    system = build_system_prompt()
    options = AgentRunOptions(verbose=verbose, quiet=quiet)

    async with officecli_tools_session() as tools:
        agent = build_agent(tools, system_prompt=system)
        result = await stream_agent(agent, user_message, options=options)
        return extract_final_text(result)
