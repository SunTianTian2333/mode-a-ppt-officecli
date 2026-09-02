from __future__ import annotations

import pytest

from src.config import PROJECT_ROOT
from src.workspace import ensure_workspace, get_output_dir, get_workspace_root, init_workspace


def test_workspace_layout():
    root = ensure_workspace()
    assert root == get_workspace_root()
    assert (root / "output").is_dir()
    assert (root / "memory").is_dir()
    assert (root / "sessions").is_dir()
    assert (root / "skills").is_dir()
    assert (root / "memory" / "MEMORY.md").is_file()


def test_default_output_under_workspace():
    out = get_output_dir()
    assert out.is_absolute()
    assert out.parent == get_workspace_root()
    assert out.name == "output"


def test_init_workspace_creates_env(tmp_path, monkeypatch):
    ws = tmp_path / "init-ws"
    monkeypatch.setenv("PPT_AGENT_HOME", str(ws))
    root = init_workspace(copy_env=True)
    assert root == ws.resolve()
    assert (root / ".env").is_file()


def test_output_dir_override_absolute(tmp_path, monkeypatch):
    custom = tmp_path / "custom-out"
    monkeypatch.setenv("PPT_OUTPUT_DIR", str(custom))
    assert get_output_dir() == custom.resolve()


def test_output_dir_override_relative(monkeypatch):
    monkeypatch.setenv("PPT_OUTPUT_DIR", "legacy-output")
    out = get_output_dir()
    assert out == (PROJECT_ROOT / "legacy-output").resolve()
