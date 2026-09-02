#!/usr/bin/env bash
# 本地验证 officecli load_skill（不经 MCP）。Agent 运行时走 MCP，见 skill_smoke.py。
set -euo pipefail
BIN="${OFFICECLI_BIN:-$HOME/.local/bin/officecli}"
echo "officecli=$("$BIN" --version)"
echo "--- load_skill pptx (first 30 lines) ---"
"$BIN" load_skill pptx | head -30
echo "--- load_skill list (first 20 lines) ---"
"$BIN" load_skill | head -20
