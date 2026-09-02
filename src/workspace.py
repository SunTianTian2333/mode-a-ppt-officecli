"""Runtime workspace layout (`.ppt-agent/`, Hermes-style)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR_NAME = ".ppt-agent"
WORKSPACE_EXAMPLE_DIR = PROJECT_ROOT / ".ppt-agent.example"

_SUBDIRS = (
    "output",
    "sessions",
    "memory",
    "skills",
    "cache",
    "transcripts",
)


def get_workspace_root() -> Path:
    raw = os.environ.get("PPT_AGENT_HOME")
    if raw:
        return Path(raw).expanduser().resolve()
    return (PROJECT_ROOT / WORKSPACE_DIR_NAME).resolve()


def get_env_path() -> Path:
    return get_workspace_root() / ".env"


def get_output_dir() -> Path:
    raw = os.environ.get("PPT_OUTPUT_DIR")
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()
    return (get_workspace_root() / "output").resolve()


def get_memory_dir() -> Path:
    return get_workspace_root() / "memory"


def get_sessions_dir() -> Path:
    return get_workspace_root() / "sessions"


def get_skills_dir() -> Path:
    return get_workspace_root() / "skills"


def get_cache_dir() -> Path:
    return get_workspace_root() / "cache"


def get_transcripts_dir() -> Path:
    return get_workspace_root() / "transcripts"


def ensure_workspace() -> Path:
    root = get_workspace_root()
    root.mkdir(parents=True, exist_ok=True)
    for name in _SUBDIRS:
        (root / name).mkdir(parents=True, exist_ok=True)
    memory_index = get_memory_dir() / "MEMORY.md"
    if not memory_index.is_file():
        memory_index.write_text(
            "# Memory index\n\n项目级持久记忆（W3）。\n",
            encoding="utf-8",
        )
    return root


def seed_business_skills_from_example() -> None:
    """Copy `.ppt-agent.example/skills/` into workspace when missing."""
    example_skills = WORKSPACE_EXAMPLE_DIR / "skills"
    target = get_skills_dir()
    target.mkdir(parents=True, exist_ok=True)
    if not example_skills.is_dir():
        return
    for entry in example_skills.iterdir():
        dest = target / entry.name
        if entry.is_dir():
            if dest.exists():
                continue
            shutil.copytree(entry, dest)
        elif entry.is_file() and not dest.exists():
            shutil.copy(entry, dest)


def init_workspace(*, copy_env: bool = True) -> Path:
    """Create `.ppt-agent/` tree; optionally seed `.env` from example."""
    root = ensure_workspace()
    env_path = get_env_path()
    example_env = WORKSPACE_EXAMPLE_DIR / ".env.example"

    if copy_env and not env_path.is_file() and example_env.is_file():
        shutil.copy(example_env, env_path)

    seed_business_skills_from_example()
    return root


def migration_hints() -> list[str]:
    hints: list[str] = []
    legacy_env = PROJECT_ROOT / ".env"
    legacy_output = PROJECT_ROOT / "output"
    if legacy_env.is_file() and not get_env_path().is_file():
        hints.append(f"legacy env found: {legacy_env} → consider .ppt-agent/.env")
    if legacy_output.is_dir() and any(legacy_output.iterdir()):
        hints.append(
            f"legacy output found: {legacy_output} → consider .ppt-agent/output/"
        )
    return hints
