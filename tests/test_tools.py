from unittest.mock import AsyncMock, patch

import pytest

from universal_actuator_mcp.server import universal_actuator, universal_status


@pytest.fixture
def mock_ctx():
    ctx = AsyncMock()
    ctx.correlation_id = "test-id"
    return ctx


@pytest.mark.asyncio
async def test_tool_universal_actuator_media_search(mock_ctx):
    payload = {"query": "test", "domain": "plex"}
    with patch("universal_actuator_mcp.server._search_federated_internal", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"results": []}
        res = await universal_actuator(domain="media", action="search", payload=payload, ctx=mock_ctx)
        assert res == {"results": []}
        mock_search.assert_called_once_with("test", "plex")


@pytest.mark.asyncio
async def test_tool_universal_actuator_system_telemetry(mock_ctx):
    with patch("universal_actuator_mcp.server._get_fleet_telemetry_internal", new_callable=AsyncMock) as mock_tel:
        mock_tel.return_value = {"status": "ok"}
        res = await universal_actuator(domain="system", action="telemetry", payload={}, ctx=mock_ctx)
        assert res == {"status": "ok"}
        mock_tel.assert_called_once()


@pytest.mark.asyncio
async def test_tool_universal_status(mock_ctx):
    with (
        patch("universal_actuator_mcp.server._get_fleet_telemetry_internal", new_callable=AsyncMock) as mock_tel,
        patch("universal_actuator_mcp.server._rag.stats", new_callable=AsyncMock) as mock_rag,
    ):
        mock_tel.return_value = {"nodes": 2}
        mock_rag.return_value = {"items": 100}

        res = await universal_status(ctx=mock_ctx)
        assert res["fleet"]["nodes"] == 2
        assert res["rag"]["items"] == 100


@pytest.mark.asyncio
async def test_tool_fallback(mock_ctx):
    res = await universal_actuator(domain="unknown", action="none", payload={}, ctx=mock_ctx)
    assert res["status"] == "partial_success"
    assert "routed via fallback" in res["message"]
