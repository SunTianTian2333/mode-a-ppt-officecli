from __future__ import annotations

from src.config import get_officecli_bin, mcp_env_for_subprocess


def test_mcp_env_excludes_ps1(monkeypatch):
    monkeypatch.setenv(
        "PS1",
        r"\[\x1b]633;A\x07\](.venv) ${debian_chroot:+($debian_chroot)}\u@\h:\w\$",
    )
    env = mcp_env_for_subprocess()
    assert "PS1" not in env


def test_mcp_env_drops_braced_placeholders(monkeypatch):
    monkeypatch.setenv("FOO", "prefix-${MISSING}-suffix")
    env = mcp_env_for_subprocess()
    assert "FOO" not in env


def test_mcp_env_has_officecli_in_path():
    env = mcp_env_for_subprocess()
    assert "PATH" in env
    assert str(get_officecli_bin().parent) in env["PATH"]
