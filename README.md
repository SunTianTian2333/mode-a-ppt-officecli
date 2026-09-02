# mode-a-ppt-officecli

LangChain Agent + OfficeCLI MCP — 生成 PPT。

**开发文档（Reference）：** [`docs/README.md`](docs/README.md)

## Phase 进度

| Step | 内容 | 状态 |
|------|------|------|
| P0 | OfficeCLI + MCP Server | ✅ |
| 1 | 骨架 + config | ✅ |
| 2 | MCP Client | ✅ |
| 3 | Skill 运行时 load + 路由 | ✅ |
| 4 | create_agent + pptx | ✅ 代码就绪（需 OPENAI_API_KEY 跑 Demo） |

## 环境

```bash
git clone https://github.com/SunTianTian2333/mode-a-ppt-officecli.git
cd mode-a-ppt-officecli
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # 填 OPENAI_API_KEY
```

依赖：OfficeCLI 已安装（`OFFICECLI_BIN`，默认 `~/.local/bin/officecli`）。

## Smoke

```bash
# Step 1 · config
python -m src.main

# Step 2 · MCP Client（自建 Agent 路径，非 Cursor）
python -m src.mcp_smoke

# Step 3 · Skill 路由 + load_skill
python -m src.skill_smoke

# 测试
pytest -q
```

期望 Step 2：

```text
mcp_smoke · step2
  tools=['officecli']
  version=1.0.146
  file=.../output/step2-smoke.pptx
  ready=step2
```

期望 Step 3：

```text
skill_smoke · step3
  system_prompt_chars=1254
  load_skill_pptx_chars=44086
  load_skill_pitch-deck_chars=65629
  load_skill_list_ok=yes
  ready=step3
```

## 目录（摘要）

```text
src/
├── main.py          # config smoke / Agent CLI
├── mcp_smoke.py     # MCP smoke
├── skill_smoke.py   # Step 3 load_skill smoke
├── mcp_client.py    # MCP Client API（含 officecli_tools_session）
├── agent.py         # Step 4 Agent
├── config.py
├── prompts/system.md
└── knowledge/README.md   # Skill 运行时 load，无静态文件
docs/                # 架构、边界、验收清单
output/              # pptx 产物（gitignore）
```

完整职责见 [架构.md](docs/架构.md)。

## Step 4 · Agent

```bash
# 需 .env 中 OPENAI_API_KEY
python -m src.main "做 3 页产品发布 PPT"

# 更详细的 tool 进度
python -m src.main --verbose "做 3 页产品发布 PPT"

# 仅打印最终回复
python -m src.main --quiet "做 3 页产品发布 PPT"

# 多轮 REPL（A-PPT-2：生成后可继续改第 N 页）
python -m src.main --chat
python -m src.main --chat --verbose
```

Agent 整轮任务在 `officecli_tools_session()` 内运行，所有 tool call 共享一个 `officecli mcp` 子进程（支持 `open` 长会话编辑）。

无参数时仍走 Step 1 config smoke：

```bash
python -m src.main
```

## 关联

- [验收清单](docs/验收清单.md)
- [能力边界](docs/能力边界.md)
- [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI)
