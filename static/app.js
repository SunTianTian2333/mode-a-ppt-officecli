const logEl = document.getElementById("log");
const promptEl = document.getElementById("prompt");
const generateBtn = document.getElementById("generate-btn");
const refreshBtn = document.getElementById("refresh-btn");
const artifactsEl = document.getElementById("artifacts");

function appendLog(text, className = "") {
  const line = document.createElement("div");
  line.className = `log-line ${className}`.trim();
  line.textContent = text;
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
}

function parseSSEChunk(buffer) {
  const events = [];
  const parts = buffer.split("\n\n");
  const rest = parts.pop() ?? "";
  for (const part of parts) {
    if (!part.trim()) continue;
    let eventType = "message";
    let data = "";
    for (const line of part.split("\n")) {
      if (line.startsWith("event:")) eventType = line.slice(6).trim();
      if (line.startsWith("data:")) data += line.slice(5).trim();
    }
    if (data) {
      try {
        events.push({ type: eventType, data: JSON.parse(data) });
      } catch {
        events.push({ type: eventType, data: { raw: data } });
      }
    }
  }
  return { events, rest };
}

function handleEvent(event) {
  const { type, data } = event;
  switch (type) {
    case "agent_turn":
      appendLog(`[agent] turn ${data.turn} · LLM…`, "agent");
      break;
    case "tool_start": {
      const slow = data.slow ? " (may take a while)" : "";
      appendLog(`[tool] ${data.command}${slow}`, "tool");
      break;
    }
    case "tool_end":
      appendLog(`  → ${data.summary}`, "tool-out");
      break;
    case "assistant":
      appendLog(data.text, "assistant");
      break;
    case "artifacts":
      renderArtifacts(data.files ?? []);
      break;
    case "done":
      appendLog(`[agent] done · ${data.tool_count} tools · ${data.elapsed_s.toFixed(1)}s`, "done");
      break;
    case "error":
      appendLog(`错误: ${data.message}`, "error");
      break;
    default:
      break;
  }
}

function renderArtifacts(files) {
  artifactsEl.innerHTML = "";
  if (!files.length) {
    const li = document.createElement("li");
    li.textContent = "暂无 pptx 文件";
    artifactsEl.appendChild(li);
    return;
  }
  for (const file of files) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = file.url;
    link.textContent = file.name;
    link.download = file.name;
    const meta = document.createElement("span");
    meta.className = "meta";
    const sizeKb = (file.size / 1024).toFixed(1);
    meta.textContent = `${sizeKb} KB`;
    li.appendChild(link);
    li.appendChild(meta);
    artifactsEl.appendChild(li);
  }
}

async function refreshArtifacts() {
  const res = await fetch("/api/artifacts");
  const data = await res.json();
  renderArtifacts(data.files ?? []);
}

async function generatePpt() {
  const message = promptEl.value.trim();
  if (!message) {
    appendLog("请输入 PPT 需求", "error");
    return;
  }

  generateBtn.disabled = true;
  logEl.innerHTML = "";
  appendLog("开始生成…", "agent");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok || !res.body) {
      appendLog(`请求失败: HTTP ${res.status}`, "error");
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parsed = parseSSEChunk(buffer);
      buffer = parsed.rest;
      for (const event of parsed.events) handleEvent(event);
    }

    if (buffer.trim()) {
      const parsed = parseSSEChunk(`${buffer}\n\n`);
      for (const event of parsed.events) handleEvent(event);
    }
  } catch (err) {
    appendLog(`网络错误: ${err}`, "error");
  } finally {
    generateBtn.disabled = false;
    await refreshArtifacts();
  }
}

generateBtn.addEventListener("click", generatePpt);
refreshBtn.addEventListener("click", refreshArtifacts);
refreshArtifacts();
