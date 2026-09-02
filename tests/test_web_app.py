from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.web.app import app


@pytest.mark.asyncio
async def test_health_endpoint(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["api_key_set"] is True
    assert "output_dir" in data


@pytest.mark.asyncio
async def test_index_and_static():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        index = await client.get("/")
        assert index.status_code == 200
        assert "PPT Agent" in index.text

        css = await client.get("/static/style.css")
        assert css.status_code == 200
        assert "color-scheme" in css.text


@pytest.mark.asyncio
async def test_artifacts_api(isolated_workspace):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/artifacts")
    assert res.status_code == 200
    assert res.json() == {"files": []}
