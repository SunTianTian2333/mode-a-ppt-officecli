# knowledge/ · 离线说明

本项目的 OfficeCLI **领域 Skill 不在此目录预置**。

## 运行时加载（Step 3+）

Agent 在改 `.pptx` 前通过 MCP 调用：

```text
officecli load_skill <pptx|pitch-deck|morph-ppt|...>
```

Skill 名称与路由规则见 [`prompts/system.md`](../prompts/system.md)。

## 本地验证（可选）

```bash
officecli load_skill pptx | head -50
python -m src.skill_smoke
```

## 为何不用静态文件灌入 system？

与 [OfficeCLI 原生设计](https://github.com/iOfficeAI/OfficeCLI) 一致：按任务匹配 skill，运行时 `load_skill`，避免锁死 `pptx` 且节省 system token。
