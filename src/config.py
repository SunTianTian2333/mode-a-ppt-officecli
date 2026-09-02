from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"

# Shell / IDE prompt vars — not needed by officecli mcp; may trigger adapter warnings.
_MCP_ENV_DROP: frozenset[str] = frozenset(
    {
        "PS1",
        "PS2",
        "PS3",
        "PS4",
        "PROMPT_COMMAND",
        "PROMPT",
        "TERMCAP",
        "TERM_PROGRAM",
        "TERM_PROGRAM_VERSION",
        "VTE_VERSION",
        "GIT_PS1_SHOWDIRTYSTATE",
        "CURSOR_TRACE_ID",
    }
)

_BRACED_VAR_RE = re.compile(r"\$\{[^}]+\}")


def _load_env_file(path: Path, *, override: bool = False) -> None:
    """Load `.env`; when override=True, skip empty values so placeholders do not wipe legacy env."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if override and not value:
            continue
        if not override and key in os.environ:
            continue
        os.environ[key] = value


def load_config() -> None:
    """Load env: legacy project `.env`, then `.ppt-agent/.env` (non-empty overrides)."""
    from src.workspace import ensure_workspace, get_workspace_root

    ensure_workspace()
    _load_env_file(PROJECT_ROOT / ".env")
    _load_env_file(get_workspace_root() / ".env", override=True)


def get_openai_settings() -> dict[str, str]:
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "base_url": os.environ.get(
            "OPENAI_BASE_URL", "https://api.deepseek.com/v1"
        ),
        "model": os.environ.get("OPENAI_MODEL", "deepseek-chat"),
    }


def get_officecli_bin() -> Path:
    raw = os.environ.get("OFFICECLI_BIN", "/home/stt/.local/bin/officecli")
    return Path(raw).expanduser()


def get_output_dir() -> Path:
    from src.workspace import get_output_dir as workspace_output_dir

    return workspace_output_dir()


def ensure_output_dir() -> Path:
    out = get_output_dir()
    out.mkdir(parents=True, exist_ok=True)
    return out


def mcp_env_for_subprocess() -> dict[str, str]:
    """Env for officecli mcp child process (no shell prompt / ${VAR} leftovers)."""
    env: dict[str, str] = {}
    for key, value in os.environ.items():
        if key in _MCP_ENV_DROP:
            continue
        if key.startswith("BASH_FUNC_"):
            continue
        if _BRACED_VAR_RE.search(value):
            continue
        env[key] = value

    bin_dir = str(get_officecli_bin().parent)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', os.defpath)}"
    return env


def officecli_mcp_connection() -> dict[str, dict[str, object]]:
    """MCP Client connection config for langchain-mcp-adapters (Step 2)."""
    return {
        "officecli": {
            "command": str(get_officecli_bin()),
            "args": ["mcp"],
            "transport": "stdio",
            "env": mcp_env_for_subprocess(),
        }
    }


def officecli_version(bin_path: Path | None = None) -> str:
    exe = bin_path or get_officecli_bin()
    if not exe.is_file():
        raise FileNotFoundError(f"officecli not found: {exe}")
    result = subprocess.run(
        [str(exe), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
