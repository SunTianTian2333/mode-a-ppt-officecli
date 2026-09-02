from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.web.artifacts import list_artifacts, resolve_download_path


def test_list_artifacts_empty(isolated_workspace):
    assert list_artifacts() == []


def test_list_artifacts_sorted_by_mtime(isolated_workspace, tmp_path, monkeypatch):
    from src.workspace import get_output_dir

    output = get_output_dir()
    output.mkdir(parents=True, exist_ok=True)
    older = output / "older.pptx"
    newer = output / "newer.pptx"
    older.write_bytes(b"x" * 10)
    newer.write_bytes(b"y" * 20)
    base = 1_700_000_000.0
    os.utime(older, (base, base))
    os.utime(newer, (base + 10, base + 10))

    files = list_artifacts()
    assert [f["name"] for f in files] == ["newer.pptx", "older.pptx"]
    assert files[0]["url"] == "/api/files/newer.pptx"


def test_resolve_download_path_ok(isolated_workspace):
    from src.workspace import get_output_dir

    output = get_output_dir()
    output.mkdir(parents=True, exist_ok=True)
    deck = output / "demo.pptx"
    deck.write_bytes(b"pptx")

    resolved = resolve_download_path("demo.pptx")
    assert resolved == deck.resolve()


@pytest.mark.parametrize(
    "filename",
    [
        "../secret.pptx",
        "../../etc/passwd",
        "foo/bar.pptx",
        "notes.txt",
        "",
    ],
)
def test_resolve_download_path_rejects_bad_names(isolated_workspace, filename):
    with pytest.raises(ValueError):
        resolve_download_path(filename)


def test_resolve_download_path_missing(isolated_workspace):
    with pytest.raises(FileNotFoundError):
        resolve_download_path("missing.pptx")
