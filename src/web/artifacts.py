"""List and download pptx artifacts from the workspace output directory."""

from __future__ import annotations

from pathlib import Path

from src.workspace import get_output_dir


def _output_dir() -> Path:
    return get_output_dir()


def list_artifacts() -> list[dict[str, object]]:
    """Return pptx files in output dir sorted by mtime (newest first)."""
    output_dir = _output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, object]] = []
    for path in sorted(output_dir.glob("*.pptx"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = path.stat()
        files.append(
            {
                "name": path.name,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "url": f"/api/files/{path.name}",
            }
        )
    return files


def resolve_download_path(filename: str) -> Path:
    """Resolve a safe download path inside the output directory."""
    if not filename or filename != Path(filename).name:
        raise ValueError("invalid filename")
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError("path traversal rejected")
    if not filename.lower().endswith(".pptx"):
        raise ValueError("only .pptx files are allowed")

    output_dir = _output_dir().resolve()
    candidate = (output_dir / filename).resolve()
    if output_dir not in candidate.parents and candidate != output_dir:
        raise ValueError("path outside output directory")
    if not candidate.is_file():
        raise FileNotFoundError(filename)
    return candidate
