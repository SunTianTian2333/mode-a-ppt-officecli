from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"


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


def officecli_mcp_connection() -> dict[str, dict[str, object]]:
    """MCP Client connection config for langchain-mcp-adapters (Step 2)."""
    env = os.environ.copy()
    bin_dir = str(get_officecli_bin().parent)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    return {
        "officecli": {
            "command": str(get_officecli_bin()),
            "args": ["mcp"],
            "transport": "stdio",
            "env": env,
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
