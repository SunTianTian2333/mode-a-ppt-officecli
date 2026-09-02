from __future__ import annotations

import pytest

from src.config import KNOWLEDGE_DIR, PROMPTS_DIR
from src.mcp_client import call_officecli, get_officecli_tools
from src.prompts.loader import load_system_prompt


def test_system_prompt_has_skill_routing():
    text = load_system_prompt()
    assert "Skill 路由" in text
    assert "load_skill" in text
    assert "pitch-deck" in text
    assert "pptx" in text
    assert "未 `load_skill`" in text or "未 load_skill" in text


def test_knowledge_dir_no_static_pptx_skill():
    assert not (KNOWLEDGE_DIR / "pptx_skill.md").exists()
    assert (KNOWLEDGE_DIR / "README.md").is_file()


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
