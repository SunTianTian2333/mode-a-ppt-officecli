"""Load Agent system prompt (Step 3: system.md only; skills via runtime load_skill)."""

from __future__ import annotations

from src.config import PROMPTS_DIR, ensure_output_dir


def load_system_prompt() -> str:
    path = PROMPTS_DIR / "system.md"
    return path.read_text(encoding="utf-8")


def build_system_prompt(*, user_message: str | None = None) -> str:
    """system.md + optional business skill (L2) + output directory."""
    from src.skills import format_business_skill_section, resolve_business_skill

    output_dir = ensure_output_dir().resolve()
    base = load_system_prompt()
    base = base.replace("/path/to/mode-a-ppt-officecli/.ppt-agent/output", str(output_dir))
    skill = resolve_business_skill(user_message)
    if skill is not None:
        base += format_business_skill_section(skill)
    return base + f"\n\n## 当前输出目录（必须使用）\n\n`{output_dir}`\n"
