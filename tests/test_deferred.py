"""Tests for deferred-batch additions: Prefab cards, resources, LLM routes, milestones REST,
error envelope, proxy probe, dialogic failure classification."""

import json
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from universal_actuator_mcp.server import (
    _discover_providers,
    _error_response,
    _maybe_proxy_to_daemon,
    agentic_workflow_tool,
    api_llm_onboarding,
    api_milestones,
    hub_status_resource,
    show_fleet_status_card,
    show_rag_stats_card,
)


@pytest.fixture
def mock_ctx():
    ctx = AsyncMock()
    ctx.correlation_id = "deferred-test"
    return ctx


@pytest.mark.asyncio
async def test_error_response_envelope():
    res = _error_response("Tool broke.", "boom", remediation="retry")
    assert res["success"] is False
    assert res["error"] == "boom"
    assert res["dialogic"]["remediation"] == "retry"


@pytest.mark.asyncio
async def test_fleet_status_card():
    with (
        patch(
            "universal_actuator_mcp.server._get_fleet_telemetry_internal",
            new_callable=AsyncMock,
        ) as mock_tel,
        patch("universal_actuator_mcp.server._rag.stats", new_callable=AsyncMock) as mock_rag,
    ):
        mock_tel.return_value = {
            "fleet_status": "Healthy",
            "active_nodes": 2,
            "total_discovered": 3,
            "host_metrics": {"cpu_percent": 10.0, "memory_percent": 20.0},
            "node_details": [{"name": "x", "port": 1, "status": "online"}],
        }
        mock_rag.return_value = {"total_items": 5}
        res = await show_fleet_status_card(None)
        assert "Healthy" in res.content[0].text
        assert res.structured_content is not None


@pytest.mark.asyncio
async def test_rag_stats_card():
    with patch("universal_actuator_mcp.server._rag.stats", new_callable=AsyncMock) as mock_rag:
        mock_rag.return_value = {"total_items": 7, "embedding_model": "test-model"}
        res = await show_rag_stats_card(None)
        assert "7 items" in res.content[0].text
        assert res.structured_content is not None


@pytest.mark.asyncio
async def test_hub_status_resource():
    with (
        patch(
            "universal_actuator_mcp.server._get_fleet_telemetry_internal",
            new_callable=AsyncMock,
        ) as mock_tel,
        patch("universal_actuator_mcp.server._rag.stats", new_callable=AsyncMock) as mock_rag,
    ):
        mock_tel.return_value = {"fleet_status": "Healthy", "active_nodes": 1}
        mock_rag.return_value = {"total_items": 2}
        payload = json.loads(await hub_status_resource())
        assert payload["service"] == "universal-actuator-mcp"
        assert payload["fleet_status"] == "Healthy"


@pytest.mark.asyncio
async def test_llm_onboarding():
    res = await api_llm_onboarding(SimpleNamespace(query_params={}))
    payload = json.loads(res.body.decode("utf-8"))
    assert payload["success"] is True
    assert payload["recommended"] == "ollama"


@pytest.mark.asyncio
async def test_milestones_rest_limit_and_bad_limit():
    with patch("universal_actuator_mcp.server._load_milestones") as mock_load:
        mock_load.return_value = [{"title": f"t{i}"} for i in range(5)]
        res = await api_milestones(SimpleNamespace(query_params={"limit": "2"}))
        assert len(json.loads(res.body.decode("utf-8"))["milestones"]) == 2
        res = await api_milestones(SimpleNamespace(query_params={"limit": "nope"}))
        assert json.loads(res.body.decode("utf-8"))["count"] == 5


@pytest.mark.asyncio
async def test_proxy_probe_no_daemon():
    with patch.dict(os.environ, {"UA_MCP_URL": "http://127.0.0.1:9/"}):
        assert await _maybe_proxy_to_daemon() is False


@pytest.mark.asyncio
async def test_discover_providers_shape():
    found = await _discover_providers()
    assert set(found) == {"ollama", "lmstudio"}
    assert "detected" in found["ollama"]


@pytest.mark.asyncio
async def test_agentic_envelope_failure_classified(mock_ctx):
    mock_ctx.sample.side_effect = [
        json.dumps({"steps": [{"step": 1, "tool": "rag_clear", "args": {}}], "expected_outcome": "x"}),
        json.dumps({"achieved": False, "quality": "failed", "issues": [], "next_steps": []}),
    ]
    with patch("universal_actuator_mcp.server._dispatch_tool", new_callable=AsyncMock) as mock_dispatch:
        mock_dispatch.return_value = {"success": False, "error": "denied", "message": "nope"}
        res = await agentic_workflow_tool(goal="Clear", ctx=mock_ctx)
        assert res["success"] is False
        assert res["data"]["steps_succeeded"] == 0
        assert res["data"]["steps_taken"][0]["status"] == "failed"
