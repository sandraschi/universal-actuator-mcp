import json
from unittest.mock import AsyncMock, patch

import pytest

from universal_actuator_mcp.server import _load_milestones, _save_milestone_internal


@pytest.mark.asyncio
async def test_health_endpoint(client):
    with patch("universal_actuator_mcp.rag.LanceDBRag.stats") as mock_stats:
        mock_stats.return_value = {"initialized": True, "total_items": 10}
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["rag"]["total_items"] == 10


@pytest.mark.asyncio
async def test_telemetry_endpoint(client):
    with patch("universal_actuator_mcp.server._get_fleet_telemetry_internal") as mock_tel:
        mock_tel.return_value = {
            "fleet_status": "Healthy",
            "active_nodes": 5,
            "total_discovered": 5,
            "host_metrics": {"cpu_percent": 10.0, "memory_percent": 50.0},
            "node_details": [],
        }

        response = await client.get("/telemetry")
        assert response.status_code == 200
        data = response.json()
        assert data["fleet_status"] == "Healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


@pytest.mark.asyncio
async def test_library_endpoint(client):
    mock_hits = {
        "results": {
            "calibre": [{"title": "Book 1", "source": "calibre"}],
            "plex": [{"title": "Movie 1", "source": "plex"}],
        }
    }
    with patch("universal_actuator_mcp.server._search_federated_internal", return_value=mock_hits):
        response = await client.get("/library?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2


@pytest.mark.asyncio
async def test_library_ingest_endpoint(client):
    mock_res = {"total_ingested": 10, "status": "success"}
    with patch("universal_actuator_mcp.server._ingest_fleet_to_rag_internal", return_value=mock_res):
        response = await client.post("/library/ingest")
        assert response.status_code == 200
        assert response.json()["total_ingested"] == 10


@pytest.mark.asyncio
async def test_chat_endpoint(client):
    response = await client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert "received: 'hello'" in response.json()["response"]


def test_milestones_logic(tmp_path):
    m_file = tmp_path / "milestones.json"
    with patch("universal_actuator_mcp.server.MILESTONES_FILE", m_file):
        # Test save
        entry = _save_milestone_internal("Title", "Desc", "achievement")
        assert entry["title"] == "Title"
        assert m_file.exists()

        # Test load
        loaded = _load_milestones()
        assert len(loaded) == 1
        assert loaded[0]["title"] == "Title"


@pytest.mark.asyncio
async def test_search_federated_internal_logic():
    from universal_actuator_mcp.server import _search_federated_internal

    with patch("universal_actuator_mcp.server._get_fleet_instance", new_callable=AsyncMock) as mock_fleet:
        mock_fleet.return_value.search_all = AsyncMock(return_value={"calibre": []})
        mock_fleet.return_value.search_calibre = AsyncMock(return_value=[{"id": 1}])

        # Test all
        res = await _search_federated_internal("test", "all")
        assert "calibre" in res["results"]

        # Test specific calibre
        res = await _search_federated_internal("test", "calibre")
        assert res["results"]["calibre"] == [{"id": 1}]


@pytest.mark.asyncio
async def test_glom_on_config_parsing(tmp_path):
    # Match the path logic in server.py
    mcp_dir = tmp_path / ".gemini" / "antigravity"
    mcp_dir.mkdir(parents=True)
    mcp_config = mcp_dir / "mcp_config.json"

    mcp_config.write_text(json.dumps({"mcpServers": {"test-server": {"command": "uv", "args": ["run"]}}}))

    with (
        patch("universal_actuator_mcp.server.os.environ", {"USERPROFILE": str(tmp_path)}),
        patch("universal_actuator_mcp.server._scan_port", return_value=None),
    ):
        from universal_actuator_mcp.server import _glom_on_internal

        res = await _glom_on_internal()
        servers = [s["name"] for s in res["discovered_servers"]]
        assert "test-server" in servers


@pytest.mark.asyncio
async def test_dispatch_tool_logic():
    from universal_actuator_mcp.server import _dispatch_tool

    with patch("universal_actuator_mcp.server._glom_on_internal", new_callable=AsyncMock) as mock_glom:
        mock_glom.return_value = {"ok": True}
        res = await _dispatch_tool("glom_on", {})
        assert res["ok"] is True

    with pytest.raises(ValueError, match="Unknown tool"):
        await _dispatch_tool("invalid", {})
