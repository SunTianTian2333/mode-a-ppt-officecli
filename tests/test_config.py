from __future__ import annotations

from pathlib import Path

import pytest

from src.config import (
    PROJECT_ROOT,
    KNOWLEDGE_DIR,
    PROMPTS_DIR,
    get_officecli_bin,
    get_output_dir,
    officecli_mcp_connection,
)


def test_project_layout():
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROMPTS_DIR / "system.md").is_file()
    assert (KNOWLEDGE_DIR / "README.md").is_file()


def test_officecli_bin_exists():
    assert get_officecli_bin().is_file()


def test_mcp_connection_shape():
    conn = officecli_mcp_connection()
    assert "officecli" in conn
    assert conn["officecli"]["transport"] == "stdio"
    assert conn["officecli"]["args"] == ["mcp"]


def test_output_dir_under_workspace():
    from src.workspace import get_workspace_root

    out = get_output_dir()
    ws = get_workspace_root()
    assert out.is_absolute()
    assert out.parent == ws
