from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from universal_actuator_mcp.fleet_aggregator import FleetAggregator


@pytest.fixture
def mock_config():
    m = MagicMock()
    m.get_server_config.return_value = {
        "scheme": "sse",
        "url": "http://localhost:10720",
        "command": "python",
        "args": ["-m", "calibre_mcp"],
    }
    return m


@pytest.mark.asyncio
async def test_aggregator_get_session_sse(mock_config):
    agg = FleetAggregator(mock_config)

    with (
        patch("universal_actuator_mcp.fleet_aggregator.sse_client") as mock_sse,
        patch("universal_actuator_mcp.fleet_aggregator.ClientSession") as mock_session,
    ):
        # Mock SSE transport
        mock_read, mock_write = MagicMock(), MagicMock()
        mock_sse.return_value.__aenter__.return_value = (mock_read, mock_write)

        # Mock MCP Session
        session_instance = AsyncMock()
        mock_session.return_value.__aenter__.return_value = session_instance

        session = await agg.get_session("calibre")

        assert session == session_instance
        assert "calibre" in agg.sessions
        session_instance.initialize.assert_called_once()
        mock_sse.assert_called_once()


@pytest.mark.asyncio
async def test_aggregator_aggregate_search(mock_config):
    agg = FleetAggregator(mock_config)

    # Mock result from one node
    mock_res = MagicMock()
    mock_res.content = [MagicMock(text='[{"id": "c1", "title": "Test Book", "authors": ["Author X"]}]')]

    with patch.object(agg, "call_tool", return_value=mock_res):
        results = await agg.aggregate_search("test", limit=5)

        assert "calibre" in results
        assert len(results["calibre"]) == 1
        assert results["calibre"][0]["title"] == "Test Book"
        assert results["calibre"][0]["source"] == "calibre"


def test_aggregator_formats():
    agg = FleetAggregator(None)

    # Calibre
    c_raw = [{"id": 1, "title": "B", "authors": ["A"], "tags": ["T"]}]
    c_fmt = agg._format_calibre_results(c_raw)
    assert c_fmt[0]["source"] == "calibre"
    assert c_fmt[0]["metadata"]["tags"] == ["T"]

    # Plex
    p_raw = {"media": [{"ratingKey": "p1", "title": "M", "type": "movie", "summary": "S"}]}
    p_fmt = agg._format_plex_results(p_raw)
    assert p_fmt[0]["source"] == "plex"
    assert p_fmt[0]["type"] == "movie"

    # Docs
    d_raw = {"data": [{"relative_path": "path/a", "content": "C", "score": 0.9}]}
    d_fmt = agg._format_docs_results(d_raw)
    assert d_fmt[0]["source"] == "docsops"
    assert d_fmt[0]["id"] == "path/a"

    # Knowledge
    k_raw = {"results": [{"id": "k1", "title": "K", "tags": ["T"]}]}
    k_fmt = agg._format_knowledge_results(k_raw)
    assert k_fmt[0]["source"] == "knowledge"

    # Immich
    i_raw = [{"id": "i1", "original_filename": "F", "created_at": "now"}]
    i_fmt = agg._format_immich_results(i_raw)
    assert i_fmt[0]["source"] == "immich"


@pytest.mark.asyncio
async def test_aggregator_timeout_handling(mock_config):
    agg = FleetAggregator(mock_config)
    with patch("universal_actuator_mcp.fleet_aggregator.sse_client", side_effect=TimeoutError):
        session = await agg.get_session("calibre")
        assert session is None


@pytest.mark.asyncio
async def test_aggregator_malformed_json(mock_config):
    agg = FleetAggregator(mock_config)
    mock_res = MagicMock()
    mock_res.content = [MagicMock(text="NOT JSON")]

    with patch.object(agg, "call_tool", return_value=mock_res):
        results = await agg.aggregate_search("test")
        assert results["calibre"] == []


@pytest.mark.asyncio
async def test_aggregator_close():
    agg = FleetAggregator(None)
    agg.exit_stack = AsyncMock()
    await agg.close()
    agg.exit_stack.aclose.assert_called_once()
    assert agg.sessions == {}
