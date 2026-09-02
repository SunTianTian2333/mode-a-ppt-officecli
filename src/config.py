from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv

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


def load_config() -> None:
    """Load .env from project root if present."""
    load_dotenv(PROJECT_ROOT / ".env")


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
    raw = os.environ.get("PPT_OUTPUT_DIR", "output")
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


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
