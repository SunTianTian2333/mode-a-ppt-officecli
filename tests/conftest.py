from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_workspace(tmp_path, monkeypatch):
    ws = tmp_path / "ppt-agent-test"
    monkeypatch.setenv("PPT_AGENT_HOME", str(ws))
    monkeypatch.delenv("PPT_OUTPUT_DIR", raising=False)

    import src.config as config_mod

    project_root = Path(__file__).resolve().parent.parent
    _real_load = config_mod._load_env_file

    def _load_env_file(path, *, override=False):
        if Path(path).resolve() == (project_root / ".env").resolve():
            return
        _real_load(path, override=override)

    monkeypatch.setattr(config_mod, "_load_env_file", _load_env_file)

    from src.workspace import seed_business_skills_from_example

    seed_business_skills_from_example()
