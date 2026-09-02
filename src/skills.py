"""Project business skills (L2) under `.ppt-agent/skills/`."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.workspace import ensure_workspace, get_skills_dir

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SKILL_FILENAME = "SKILL.md"


@dataclass(frozen=True)
class BusinessSkill:
    id: str
    title: str
    capability_skills: tuple[str, ...]
    triggers: tuple[str, ...]
    body: str
    path: Path


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw = match.group(1)
    body = text[match.end() :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body


def _split_csv(value: str) -> tuple[str, ...]:
    parts = [part.strip() for part in value.replace("[", "").replace("]", "").split(",")]
    return tuple(part for part in parts if part)


def _load_skill_file(skill_dir: Path) -> BusinessSkill | None:
    skill_path = skill_dir / _SKILL_FILENAME
    if not skill_path.is_file():
        return None
    text = skill_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    skill_id = meta.get("name") or skill_dir.name
    title = meta.get("title") or skill_id
    capability = _split_csv(meta.get("capability_skills", "pptx"))
    triggers = _split_csv(meta.get("triggers", ""))
    return BusinessSkill(
        id=skill_id,
        title=title,
        capability_skills=capability or ("pptx",),
        triggers=triggers,
        body=body.strip(),
        path=skill_path,
    )


def list_business_skills() -> list[BusinessSkill]:
    ensure_workspace()
    root = get_skills_dir()
    if not root.is_dir():
        return []
    skills: list[BusinessSkill] = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        loaded = _load_skill_file(entry)
        if loaded is not None:
            skills.append(loaded)
    return skills


def _message_matches_triggers(message: str, triggers: tuple[str, ...]) -> bool:
    lowered = message.lower()
    for trigger in triggers:
        token = trigger.strip().lower()
        if token and token in lowered:
            return True
    return False


def match_business_skill(
    user_message: str,
    skills: list[BusinessSkill] | None = None,
) -> BusinessSkill | None:
    catalog = skills if skills is not None else list_business_skills()
    if not catalog:
        return None
    for skill in catalog:
        if skill.triggers and _message_matches_triggers(user_message, skill.triggers):
            return skill
    return None


def resolve_business_skill(user_message: str | None = None) -> BusinessSkill | None:
    """Pick business skill for this turn; single-skill workspace defaults to it."""
    catalog = list_business_skills()
    if not catalog:
        return None
    if user_message:
        matched = match_business_skill(user_message, catalog)
        if matched is not None:
            return matched
    if len(catalog) == 1:
        return catalog[0]
    return None


def format_business_skill_section(skill: BusinessSkill) -> str:
    caps = ", ".join(f"`{name}`" for name in skill.capability_skills)
    return (
        f"\n\n## 当前业务 skill · {skill.title}\n\n"
        f"- id: `{skill.id}`\n"
        f"- capability_skills: {caps}（改文件前 `officecli load_skill` 其中之一）\n\n"
        f"{skill.body}\n"
    )
