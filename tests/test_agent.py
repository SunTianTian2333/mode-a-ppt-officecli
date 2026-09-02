from __future__ import annotations

import pytest

from src.config import ensure_output_dir, get_openai_settings, load_config
from src.prompts.loader import build_system_prompt, load_system_prompt


def test_build_system_prompt_injects_output_dir():
    output_dir = ensure_output_dir().resolve()
    text = build_system_prompt()
    assert str(output_dir) in text
    assert "当前输出目录" in text
    assert "/path/to/mode-a-ppt-officecli/output" not in text


def test_load_system_prompt_unchanged_template():
    raw = load_system_prompt()
    assert "/path/to/mode-a-ppt-officecli/output" in raw


@pytest.mark.asyncio
async def test_run_ppt_agent_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    load_config()

    from src.agent import run_ppt_agent

    settings = get_openai_settings()
    assert not settings["api_key"]

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        await run_ppt_agent("做 3 页 PPT")
