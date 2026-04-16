from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from universal_actuator_mcp.fleet import FleetManager


@pytest.fixture
def fleet():
    return FleetManager()


@pytest.mark.asyncio
async def test_fleet_manager_is_port_open(fleet):
    with patch("socket.socket") as mock_socket:
        # Simulate port open
        mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 0
        assert fleet.is_port_open("127.0.0.1", 10720) is True

        # Simulate port closed
        mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 111
        assert fleet.is_port_open("127.0.0.1", 10720) is False


@pytest.mark.asyncio
async def test_fleet_manager_ensure_all(fleet):
    """Test the ensure_all loop logic."""
    mock_config = {
        "calibre": {"url": "127.0.0.1:10720", "scheme": "sse", "args": ["-m", "calibre"]},
    }
    with (
        patch.object(fleet._cfg_manager, "get_mcp_servers", return_value=mock_config),
        patch.object(fleet, "is_port_open", side_effect=[False, True]),
        patch.object(fleet, "_start_node_headless", return_value=True),
    ):
        results = await fleet.ensure_all()
        assert results["calibre"] == "starting"


@pytest.mark.asyncio
async def test_fleet_manager_ingest_all_to_rag(fleet):
    mock_rag = AsyncMock()
    mock_rag.ingest_items.return_value = 10

    mock_items = [{"id": "1", "title": "Item", "source": "calibre"}]

    with (
        patch.object(fleet, "list_calibre", return_value=mock_items),
        patch.object(fleet, "list_plex", return_value=[]),
        patch.object(fleet, "list_immich", return_value=[]),
        patch.object(fleet, "list_docs", return_value=[]),
        patch.object(fleet, "list_knowledge", return_value=[]),
    ):
        counts = await fleet.ingest_all_to_rag(mock_rag, limit=10)
        assert counts["calibre"] == 1
        assert counts["total"] == 10
        mock_rag.ingest_items.assert_called_once()


@pytest.mark.asyncio
async def test_fleet_manager_search_methods(fleet):
    mock_results = {"calibre": [{"title": "C"}], "plex": [{"title": "P"}]}
    with patch.object(fleet._fleet, "aggregate_search", return_value=mock_results):
        # All search methods route to aggregator
        assert await fleet.search_calibre("test") == [{"title": "C"}]
        assert await fleet.search_plex("test") == [{"title": "P"}]
        assert await fleet.search_immich("test") == []
        assert await fleet.search_all("test") == mock_results


@pytest.mark.asyncio
async def test_fleet_manager_source_listings(fleet):
    mock_results = {"calibre": [{"id": 1}], "plex": [{"id": "p1"}], "immich": [{"id": "i1"}]}
    with patch.object(fleet._fleet, "aggregate_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_results

        # Calibre
        res = await fleet.list_calibre(limit=1)
        assert res[0]["id"] == 1

        # Plex
        res = await fleet.list_plex(limit=1)
        assert res[0]["id"] == "p1"

        # Immich
        res = await fleet.list_immich(limit=1)
        assert res[0]["id"] == "i1"


@pytest.mark.asyncio
async def test_fleet_manager_close(fleet):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    fleet._processes["dummy"] = mock_proc

    with patch.object(fleet._fleet, "close", new_callable=AsyncMock) as mock_agg_close:
        await fleet.close()
        mock_agg_close.assert_called_once()
        mock_proc.terminate.assert_called_once()
        assert len(fleet._processes) == 0
