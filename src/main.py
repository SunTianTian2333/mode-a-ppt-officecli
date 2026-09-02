"""CLI entry: config smoke (no args) or PPT Agent (user message)."""

from __future__ import annotations

import asyncio
import sys

from src.config import (
    ensure_output_dir,
    get_officecli_bin,
    get_openai_settings,
    get_output_dir,
    load_config,
    officecli_version,
)


def run_config_smoke() -> int:
    load_config()
    settings = get_openai_settings()
    officecli_bin = get_officecli_bin()
    output_dir = ensure_output_dir()

    has_api_key = bool(settings["api_key"])
    officecli_ok = officecli_bin.is_file()
    version = officecli_version() if officecli_ok else "missing"

    print("mode-a-ppt-officecli · step1 config smoke")
    print(f"  model={settings['model']}")
    print(f"  base_url={settings['base_url']}")
    print(f"  api_key={'set' if has_api_key else 'NOT SET'}")
    print(f"  officecli={officecli_bin}")
    print(f"  officecli_version={version}")
    print(f"  output={output_dir.resolve()}")
    print(f"  ready=step1")

    if not officecli_ok:
        print("  error: officecli binary missing", file=sys.stderr)
        return 1
    return 0


async def main_async(argv: list[str]) -> int:
    if len(argv) > 1:
        from src.agent import run_ppt_agent

        user_message = " ".join(argv[1:])
        try:
            print("mode-a-ppt-officecli · agent")
            reply = await run_ppt_agent(user_message)
            print(reply)
            return 0
        except ValueError as exc:
            print(f"  error: {exc}", file=sys.stderr)
            return 1
    return run_config_smoke()


def main() -> int:
    return asyncio.run(main_async(sys.argv))


if __name__ == "__main__":
    raise SystemExit(main())
