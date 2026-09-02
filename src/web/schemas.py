"""Request/response models for the web API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str | None = None  # reserved for W-Web-2


class ArtifactInfo(BaseModel):
    name: str
    size: int
    mtime: float
    url: str


class HealthResponse(BaseModel):
    ok: bool
    api_key_set: bool
    officecli_ok: bool
    output_dir: str
