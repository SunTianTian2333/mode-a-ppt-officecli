"""Step 3 smoke: runtime load_skill via MCP + system prompt."""

from __future__ import annotations

import asyncio
import sys

from src.config import load_config
from src.mcp_client import call_officecli, officecli_tools_session
from src.prompts.loader import load_system_prompt


async def run_smoke() -> int:
    load_config()
    print("skill_smoke · step3")

    async with officecli_tools_session() as tools:
        system = load_system_prompt()
        if "Skill 路由" not in system or "load_skill" not in system:
            print("  error: system.md missing skill routing", file=sys.stderr)
            return 1
        print(f"  system_prompt_chars={len(system)}")

        for skill_name, needle in (
            ("pptx", "officecli-pptx"),
            ("pitch-deck", "pitch"),
        ):
            text = await call_officecli(
                f"officecli load_skill {skill_name}", tools=tools
            )
            if len(text) < 500:
                print(f"  error: load_skill {skill_name} too short", file=sys.stderr)
                return 1
            if needle.lower() not in text.lower() and skill_name not in text.lower():
                print(
                    f"  error: load_skill {skill_name} unexpected content",
                    file=sys.stderr,
                )
                return 1
            print(f"  load_skill_{skill_name}_chars={len(text)}")

        list_text = await call_officecli("officecli load_skill", tools=tools)
        if "pptx" not in list_text.lower():
            print("  error: load_skill list missing pptx", file=sys.stderr)
            return 1
        print("  load_skill_list_ok=yes")

    print("  ready=step3")
    return 0


def main() -> int:
    return asyncio.run(run_smoke())


if __name__ == "__main__":
    raise SystemExit(main())
