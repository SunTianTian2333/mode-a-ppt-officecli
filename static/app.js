const chatEl = document.getElementById("chat");
const emptyStateEl = document.getElementById("empty-state");
const promptEl = document.getElementById("prompt");
const generateBtn = document.getElementById("generate-btn");
const refreshBtn = document.getElementById("refresh-btn");
const artifactsEl = document.getElementById("artifacts");
const exampleChips = document.getElementById("example-chips");

let progressBlock = null;
let progressStepsEl = null;
let progressHeadEl = null;

function hideEmptyState() {
  emptyStateEl?.classList.add("hidden");
}

function autoResizeTextarea() {
  promptEl.style.height = "auto";
  promptEl.style.height = `${Math.min(promptEl.scrollHeight, 140)}px`;
}

function appendMessage(role, text, label) {
  hideEmptyState();
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  if (label) {
    const lbl = document.createElement("div");
    lbl.className = "msg-label";
    lbl.textContent = label;
    wrap.appendChild(lbl);
  }

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);

  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  return wrap;
}

function ensureProgressBlock() {
  if (progressBlock) return;

  hideEmptyState();
  progressBlock = document.createElement("div");
  progressBlock.className = "progress-block";

  progressHeadEl = document.createElement("div");
  progressHeadEl.className = "progress-head";
  progressHeadEl.innerHTML = '<span class="dot"></span><span>正在生成…</span>';

  progressStepsEl = document.createElement("div");
  progressStepsEl.className = "progress-steps";

  progressBlock.appendChild(progressHeadEl);
  progressBlock.appendChild(progressStepsEl);
  chatEl.appendChild(progressBlock);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function appendProgressStep(text, className = "progress-step") {
  ensureProgressBlock();
  const step = document.createElement("div");
  step.className = className;
  step.textContent = text;
  progressStepsEl.appendChild(step);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function finishProgress(toolCount, elapsedS) {
  if (!progressBlock) return;
  progressHeadEl.classList.add("done");
  progressHeadEl.lastElementChild.textContent = "生成完成";
  appendProgressStep(
    `${toolCount} 次工具调用 · ${elapsedS.toFixed(1)} 秒`,
    "progress-step done-line",
  );
  progressBlock = null;
  progressStepsEl = null;
  progressHeadEl = null;
}

function resetProgress() {
  progressBlock = null;
  progressStepsEl = null;
  progressHeadEl = null;
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
      appendProgressStep(`思考中 · 第 ${data.turn} 轮`, "progress-step");
      break;
    case "tool_start": {
      const slow = data.slow ? " · 可能需要稍等" : "";
      const cmd = data.command.length > 100 ? `${data.command.slice(0, 100)}…` : data.command;
      appendProgressStep(`${cmd}${slow}`, "progress-step tool");
      break;
    }
    case "tool_end":
      appendProgressStep(data.summary, "progress-step tool-out");
      break;
    case "assistant":
      appendMessage("assistant", data.text, "Assistant");
      break;
    case "artifacts":
      renderArtifacts(data.files ?? []);
      break;
    case "done":
      finishProgress(data.tool_count, data.elapsed_s);
      break;
    case "error":
      appendMessage("error", data.message, "错误");
      resetProgress();
      break;
    default:
      break;
  }
}

function renderArtifacts(files) {
  artifactsEl.innerHTML = "";
  if (!files.length) {
    const li = document.createElement("li");
    li.className = "empty-item";
    li.textContent = "暂无 pptx";
    artifactsEl.appendChild(li);
    return;
  }

  for (const file of files) {
    const li = document.createElement("li");
    const card = document.createElement("div");
    card.className = "artifact-card";

    const icon = document.createElement("div");
    icon.className = "file-icon";
    icon.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>';

    const info = document.createElement("div");
    info.className = "file-info";

    const name = document.createElement("a");
    name.className = "file-name";
    name.href = file.url;
    name.textContent = file.name;
    name.title = file.name;

    const meta = document.createElement("span");
    meta.className = "file-meta";
    meta.textContent = `${(file.size / 1024).toFixed(1)} KB`;

    info.appendChild(name);
    info.appendChild(meta);

    const download = document.createElement("a");
    download.className = "download-btn";
    download.href = file.url;
    download.download = file.name;
    download.title = "下载";
    download.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>';

    card.appendChild(icon);
    card.appendChild(info);
    card.appendChild(download);
    li.appendChild(card);
    artifactsEl.appendChild(li);
  }
}

async function refreshArtifacts() {
  const res = await fetch("/api/artifacts");
  const data = await res.json();
  renderArtifacts(data.files ?? []);
}

function clearPrompt() {
  promptEl.value = "";
  promptEl.style.height = "auto";
}

async function generatePpt() {
  const message = promptEl.value.trim();
  if (!message) return;

  generateBtn.disabled = true;
  resetProgress();
  appendMessage("user", message, "You");
  clearPrompt();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok || !res.body) {
      appendMessage("error", `请求失败: HTTP ${res.status}`, "错误");
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
    appendMessage("error", `网络错误: ${err}`, "错误");
    resetProgress();
  } finally {
    generateBtn.disabled = false;
    await refreshArtifacts();
  }
}

generateBtn.addEventListener("click", generatePpt);
refreshBtn.addEventListener("click", refreshArtifacts);

promptEl.addEventListener("input", autoResizeTextarea);

promptEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!generateBtn.disabled) generatePpt();
  }
});

exampleChips?.addEventListener("click", (e) => {
  const chip = e.target.closest(".chip");
  if (!chip) return;
  promptEl.value = chip.dataset.prompt ?? "";
  autoResizeTextarea();
  promptEl.focus();
});

autoResizeTextarea();
refreshArtifacts();
