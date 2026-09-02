from __future__ import annotations

from pathlib import Path

import pytest

from src.config import (
    PROJECT_ROOT,
    PROMPTS_DIR,
    get_officecli_bin,
    get_output_dir,
    officecli_mcp_connection,
)


def test_project_layout():
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROMPTS_DIR / "system.md").is_file()
    assert (PROJECT_ROOT / ".ppt-agent.example").is_dir()


def test_officecli_bin_exists():
    assert get_officecli_bin().is_file()


def test_mcp_connection_shape():
    conn = officecli_mcp_connection()
    assert "officecli" in conn
    assert conn["officecli"]["transport"] == "stdio"
    assert conn["officecli"]["args"] == ["mcp"]


def test_recursion_limit_default(monkeypatch):
    from src.config import DEFAULT_RECURSION_LIMIT, agent_run_config, get_recursion_limit

    monkeypatch.delenv("PPT_RECURSION_LIMIT", raising=False)
    assert get_recursion_limit() == DEFAULT_RECURSION_LIMIT
    assert agent_run_config() == {"recursion_limit": DEFAULT_RECURSION_LIMIT}


def test_recursion_limit_env_override(monkeypatch):
    from src.config import agent_run_config, get_recursion_limit

    monkeypatch.setenv("PPT_RECURSION_LIMIT", "200")
    assert get_recursion_limit() == 200
    assert agent_run_config() == {"recursion_limit": 200}


def test_output_dir_under_workspace():
    from src.workspace import get_workspace_root

    out = get_output_dir()
    ws = get_workspace_root()
    assert out.is_absolute()
    assert out.parent == ws
