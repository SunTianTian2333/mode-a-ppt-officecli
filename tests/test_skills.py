from __future__ import annotations

from src.prompts.loader import build_system_prompt, load_system_prompt
from src.skills import (
    list_business_skills,
    match_business_skill,
    resolve_business_skill,
)


def test_list_business_skills_includes_shell():
    skills = list_business_skills()
    assert len(skills) >= 1
    assert any(skill.id == "business-ppt" for skill in skills)


def test_match_business_ppt_by_trigger():
    skill = match_business_skill("做一个 LangChain 教学 PPT")
    assert skill is not None
    assert skill.id == "business-ppt"
    assert skill.capability_skills == ("pptx",)


def test_resolve_defaults_single_skill():
    skill = resolve_business_skill()
    assert skill is not None
    assert skill.title == "业务ppt"


def test_build_system_prompt_injects_business_skill():
    text = build_system_prompt(user_message="做 PPT")
    assert "当前业务 skill" in text
    assert "业务ppt" in text
    assert "capability_skills: `pptx`" in text


def test_system_prompt_is_thin():
    raw = load_system_prompt()
    assert "Skill 路由" not in raw
    assert "pitch-deck" not in raw
    assert len(raw.splitlines()) <= 30
