"""Load Agent system prompt (Step 3: system.md only; skills via runtime load_skill)."""

from __future__ import annotations

from src.config import PROMPTS_DIR, ensure_output_dir


def load_system_prompt() -> str:
    path = PROMPTS_DIR / "system.md"
    return path.read_text(encoding="utf-8")


def build_system_prompt() -> str:
    """system.md with the real output/ absolute path injected for the Agent."""
    output_dir = ensure_output_dir().resolve()
    base = load_system_prompt()
    base = base.replace("/path/to/mode-a-ppt-officecli/output", str(output_dir))
    return base + f"\n\n## 当前输出目录（必须使用）\n\n`{output_dir}`\n"
