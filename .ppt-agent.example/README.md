# `.ppt-agent/` 工作区模板

复制到项目根后由 `python -m src.main --init-workspace` 自动创建 `.ppt-agent/`。

```text
.ppt-agent/
├── .env           ← 从本目录 .env.example 复制
├── output/        ← pptx 产物
├── sessions/      ← W2：会话持久化
├── memory/        ← W3：持久记忆
├── skills/        ← W4：项目级扩展 skill
├── cache/         ← W4：load_skill 缓存
└── transcripts/   ← 可选：大 tool 输出归档
```

整个 `.ppt-agent/` 已在 `.gitignore` 中，勿提交密钥。
