from __future__ import annotations

import pytest

from src.config import PROMPTS_DIR
from src.mcp_client import call_officecli, get_officecli_tools
from src.prompts.loader import build_system_prompt, load_system_prompt
from src.workspace import ensure_workspace, get_skills_dir


def test_system_prompt_mentions_load_skill_flow():
    text = load_system_prompt()
    assert "load_skill" in text
    assert "officecli" in text


def test_build_system_prompt_includes_capability_via_business_skill():
    text = build_system_prompt(user_message="做 PPT")
    assert "capability_skills" in text
    assert "`pptx`" in text


def test_skills_dir_no_static_pptx_skill():
    ensure_workspace()
    assert not (get_skills_dir() / "pptx_skill.md").exists()


def test_system_md_exists():
    assert (PROMPTS_DIR / "system.md").is_file()


@pytest.mark.asyncio
async def test_load_skill_pptx_via_mcp():
    tools = await get_officecli_tools()
    text = await call_officecli("officecli load_skill pptx", tools=tools)
    assert len(text) > 500
    assert "help" in text.lower() or "pptx" in text.lower()


@pytest.mark.asyncio
async def test_load_skill_pitch_deck_via_mcp():
    tools = await get_officecli_tools()
    text = await call_officecli("officecli load_skill pitch-deck", tools=tools)
    assert len(text) > 200
