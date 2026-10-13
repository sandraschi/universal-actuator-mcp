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
        mock_search.return_value = {"results": [], "total_hits": 0}
        res = await universal_actuator(domain="media", action="search", payload=payload, ctx=mock_ctx)
        assert res["success"] is True
        assert res["data"] == {"results": [], "total_hits": 0}
        assert "0 hits" in res["message"]
        mock_search.assert_called_once_with("test", "plex")


@pytest.mark.asyncio
async def test_tool_universal_actuator_system_telemetry(mock_ctx):
    with patch("universal_actuator_mcp.server._get_fleet_telemetry_internal", new_callable=AsyncMock) as mock_tel:
        mock_tel.return_value = {"fleet_status": "Healthy"}
        res = await universal_actuator(domain="system", action="telemetry", payload={}, ctx=mock_ctx)
        assert res["success"] is True
        assert res["data"] == {"fleet_status": "Healthy"}
        mock_tel.assert_called_once()


@pytest.mark.asyncio
async def test_tool_universal_status(mock_ctx):
    with (
        patch("universal_actuator_mcp.server._get_fleet_telemetry_internal", new_callable=AsyncMock) as mock_tel,
        patch("universal_actuator_mcp.server._rag.stats", new_callable=AsyncMock) as mock_rag,
    ):
        mock_tel.return_value = {"fleet_status": "Healthy"}
        mock_rag.return_value = {"total_items": 100}

        res = await universal_status(ctx=mock_ctx)
        assert res["success"] is True
        assert res["data"]["fleet"]["fleet_status"] == "Healthy"
        assert res["data"]["rag"]["total_items"] == 100


@pytest.mark.asyncio
async def test_tool_fallback(mock_ctx):
    res = await universal_actuator(domain="unknown", action="none", payload={}, ctx=mock_ctx)
    assert res["success"] is True
    assert res["data"]["routing_key"] == "unknown.none"
    assert "routed via fallback" in res["message"]


@pytest.mark.asyncio
async def test_dialogic_envelope_keys(mock_ctx):
    """Every dialogic tool result carries success + message + data."""
    res = await universal_actuator(domain="unknown", action="none", payload={}, ctx=mock_ctx)
    assert set(res) == {"success", "message", "data"}
