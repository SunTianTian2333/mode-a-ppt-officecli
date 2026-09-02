# Spec: mode-a-ppt-officecli（LangChain + MCP + PPT）

Status: in_progress
Category: project
Created: 2026-09-02

## Problem

需要在 agent-career 内落地第一个 **自建 LangChain Agent** Demo：通过 MCP Client 操作 OfficeCLI 生成 PPT，并与手搓 `mini-harness-ts` 形成对照，服务求职叙事（模式 A-PPT）。

## 目标

1. 独立 Python Agent 进程连通 `officecli mcp`（不依赖 Cursor Agent）
2. Step 3 运行时 Skill 路由 + `load_skill`；Step 4 `create_agent` 产出 ≥3 页 pptx
3. 项目 docs 齐全：架构、边界、验收清单（[`docs/langchain-agent-patterns/mode-a-ppt-officecli/`](../../langchain-agent-patterns/mode-a-ppt-officecli/README.md)）

## 非目标

- LangGraph 验收图、RAG、多 Agent（后续 Spec）
- Web UI、生产 OA 对接
- 修改 mini-harness-ts / dsh 上游

## 范围

- 允许：`projects/langchain-agent-patterns/mode-a-ppt-officecli/**` · `docs/langchain-agent-patterns/mode-a-ppt-officecli/**` · `learning/phase-4-langchain-patterns/**` · 本 Spec
- 禁止：`projects/mini-harness-ts/**` · `projects/deepseek-harness/**` · `/home/stt/work/**`

## 方案（Decision · 随 Step 更新）

| Step | 内容 | 状态 |
|------|------|------|
| P0 | OfficeCLI 安装 + MCP Server smoke | ✅ |
| 1 | pyproject + config + 占位 | ✅ |
| 2 | `mcp_client` + `mcp_smoke` + 测试 | ✅ |
| 3 | Skill 路由 + 运行时 `load_skill`（非静态文件） | ✅ |
| 4 | `create_agent` + CLI 入口 + 长 session | ✅ 代码；Demo 待 Key |

技术栈：LangChain `create_agent` · `langchain-mcp-adapters` · DeepSeek API · OfficeCLI MCP。

## 曾考虑的替代方案

- **Cursor 内置 Agent + mcp.json** → 不选，目标是自建 Agent 进程  
- **Shell Tool 直接 bash officecli** → 不选，与选定 MCP + Skill 栈一致  
- **Step 4 直接用 LangGraph** → 不选，MVP 先用 `create_agent`  

## 验收标准

见 [`验收清单.md`](../../langchain-agent-patterns/mode-a-ppt-officecli/验收清单.md)。Step 4 全部勾选后本 Spec 移 `done/`。

## 风险与放弃

- OfficeCLI / LangChain API 变更 — 锁定版本于 README，Skill 可重导  
- MCP 每 call 新 session 可能慢 — Step 4 已用 `officecli_tools_session()`；smoke 亦迁移  

---

## 实际交付

| 项 | 内容 |
|----|------|
| 完成日期 | 2026-09-02（Step 4 代码；A-PPT-1 Demo 待 Key） |
| 变更文件 | Step 4：`mcp_client.py`（`officecli_tools_session`）· `agent.py` · `main.py` · `prompts/loader.py` · `tests/test_agent.py` · `tests/test_mcp_client.py`；smoke 迁长 session |
| 与方案差异 | P0 曾注册 Cursor MCP；Step 3 运行时 load_skill；Step 4 MCP 长 session（非 get_tools 便捷模式） |
| 未解决 | A-PPT-1 三页 Demo 实测；Spec 移 done/ |
