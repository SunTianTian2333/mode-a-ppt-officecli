"""Step 2 smoke: MCP Client → officecli mcp → tool invoke."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from src.config import ensure_output_dir, load_config
from src.mcp_client import OFFICECLI_TOOL_NAME, call_officecli, officecli_tools_session


async def run_smoke() -> int:
    load_config()
    output_dir = ensure_output_dir()
    pptx_path = output_dir / "step2-smoke.pptx"
    if pptx_path.exists():
        pptx_path.unlink()

    async with officecli_tools_session() as tools:
        tool_names = [t.name for t in tools]
        print("mcp_smoke · step2")
        print(f"  tools={tool_names}")

        if OFFICECLI_TOOL_NAME not in tool_names and not any(
            n.endswith(f"_{OFFICECLI_TOOL_NAME}") for n in tool_names
        ):
            print("  error: officecli tool missing", file=sys.stderr)
            return 1

        version_text = await call_officecli("officecli --version", tools=tools)
        print(f"  version={version_text.strip()}")

        create_cmd = f"officecli create {pptx_path.resolve()}"
        create_text = await call_officecli(create_cmd, tools=tools)
        print(f"  create={create_text.splitlines()[0] if create_text else 'ok'}")

    if not pptx_path.is_file() or pptx_path.stat().st_size == 0:
        print(f"  error: file not created: {pptx_path}", file=sys.stderr)
        return 1

    size = pptx_path.stat().st_size
    print(f"  file={pptx_path.resolve()} ({size} bytes)")
    print("  ready=step2")
    return 0


def main() -> int:
    return asyncio.run(run_smoke())


if __name__ == "__main__":
    raise SystemExit(main())
