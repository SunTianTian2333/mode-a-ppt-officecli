"""FastAPI application for W-Web-1 demo."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from src.config import ensure_output_dir, get_officecli_bin, get_openai_settings, load_config
from src.web.artifacts import list_artifacts, resolve_download_path
from src.web.schemas import ChatRequest, HealthResponse
from src.web.service import chat_sse
from src.workspace import get_output_dir

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_config()
    ensure_output_dir()
    yield


app = FastAPI(title="mode-a-ppt-officecli", version="0.1.0", lifespan=lifespan)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/static/{path:path}")
async def static_files(path: str) -> FileResponse:
    file_path = (STATIC_DIR / path).resolve()
    if STATIC_DIR.resolve() not in file_path.parents and file_path != STATIC_DIR.resolve():
        raise HTTPException(status_code=404, detail="not found")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(file_path)


@app.post("/api/chat")
async def chat(body: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        chat_sse(body.message.strip()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/artifacts")
async def artifacts() -> dict[str, object]:
    return {"files": list_artifacts()}


@app.get("/api/files/{filename}")
async def download_file(filename: str) -> FileResponse:
    try:
        path = resolve_download_path(filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    load_config()
    settings = get_openai_settings()
    officecli_ok = get_officecli_bin().is_file()
    api_key_set = bool(settings["api_key"])
    return HealthResponse(
        ok=officecli_ok and api_key_set,
        api_key_set=api_key_set,
        officecli_ok=officecli_ok,
        output_dir=str(get_output_dir()),
    )
