"""CLI entry: config smoke (no args) or PPT Agent (user message)."""

from __future__ import annotations

import argparse
import asyncio
import sys

from src.config import (
    ensure_output_dir,
    get_officecli_bin,
    get_openai_settings,
    load_config,
    officecli_version,
)
from src.workspace import get_env_path, get_output_dir, get_workspace_root, init_workspace, migration_hints


def run_config_smoke() -> int:
    load_config()
    settings = get_openai_settings()
    officecli_bin = get_officecli_bin()
    output_dir = ensure_output_dir()
    workspace = get_workspace_root()

    has_api_key = bool(settings["api_key"])
    officecli_ok = officecli_bin.is_file()
    version = officecli_version() if officecli_ok else "missing"

    print("mode-a-ppt-officecli · step1 config smoke")
    print(f"  model={settings['model']}")
    print(f"  base_url={settings['base_url']}")
    print(f"  api_key={'set' if has_api_key else 'NOT SET'}")
    print(f"  officecli={officecli_bin}")
    print(f"  officecli_version={version}")
    print(f"  workspace={workspace}")
    print(f"  env_file={get_env_path()}")
    print(f"  output={output_dir.resolve()}")
    print(f"  ready=step1")

    for hint in migration_hints():
        print(f"  hint: {hint}")

    if not officecli_ok:
        print("  error: officecli binary missing", file=sys.stderr)
        return 1
    return 0


def run_init_workspace() -> int:
    root = init_workspace(copy_env=True)
    print("mode-a-ppt-officecli · init workspace")
    print(f"  workspace={root}")
    print(f"  env={get_env_path()}")
    print(f"  output={get_output_dir()}")
    if get_env_path().is_file():
        print("  env_status=ready (edit OPENAI_API_KEY)")
    else:
        print("  env_status=missing (copy .ppt-agent.example/.env.example)")
    for hint in migration_hints():
        print(f"  hint: {hint}")
    print("  ready=workspace")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LangChain Agent + OfficeCLI MCP for PPT generation",
    )
    parser.add_argument(
        "message",
        nargs="*",
        help="User request for the PPT agent (omit for config smoke)",
    )
    parser.add_argument(
        "--init-workspace",
        action="store_true",
        help="Create .ppt-agent/ runtime workspace",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Interactive multi-turn REPL",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose tool progress output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print the final assistant reply (single-turn)",
    )
    return parser


async def main_async(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    if args.init_workspace:
        return run_init_workspace()

    if args.chat and args.message:
        print("  error: use either --chat or a one-shot message, not both", file=sys.stderr)
        return 1

    try:
        if args.chat:
            from src.repl import run_ppt_chat

            return await run_ppt_chat(verbose=args.verbose, quiet=args.quiet)

        if args.message:
            from src.agent import run_ppt_agent

            user_message = " ".join(args.message)
            if not args.quiet:
                print("mode-a-ppt-officecli · agent")
            reply = await run_ppt_agent(
                user_message,
                verbose=args.verbose,
                quiet=args.quiet,
            )
            print(reply)
            return 0
    except ValueError as exc:
        print(f"  error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"  error: {exc}", file=sys.stderr)
        return 1

    return run_config_smoke()


def main() -> int:
    return asyncio.run(main_async(sys.argv))


if __name__ == "__main__":
    raise SystemExit(main())
