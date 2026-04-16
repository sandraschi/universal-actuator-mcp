import json
from unittest.mock import AsyncMock, patch

import pytest

from universal_actuator_mcp.server import agentic_workflow_tool


@pytest.fixture
def mock_ctx():
    ctx = AsyncMock()
    ctx.correlation_id = "agentic-test"
    # Mock sample to return a valid JSON plan
    ctx.sample.side_effect = [
        # Plan response
        json.dumps(
            {
                "steps": [{"step": 1, "tool": "get_fleet_telemetry", "args": {}, "rationale": "initial check"}],
                "expected_outcome": "Complete telemetry audit",
            }
        ),
        # Audit response
        json.dumps({"achieved": True, "quality": "good", "issues": [], "next_steps": []}),
    ]
    return ctx


@pytest.mark.asyncio
async def test_agentic_workflow_success(mock_ctx):
    with patch("universal_actuator_mcp.server._dispatch_tool", new_callable=AsyncMock) as mock_dispatch:
        mock_dispatch.return_value = {"nodes": 5}

        res = await agentic_workflow_tool(goal="Audit fleet", ctx=mock_ctx)

        assert res["goal"] == "Audit fleet"
        assert res["steps_executed"] == 1
        assert res["steps_succeeded"] == 1
        assert res["audit"]["achieved"] is True
        mock_dispatch.assert_called_once_with("get_fleet_telemetry", {})


@pytest.mark.asyncio
async def test_agentic_workflow_plan_failure(mock_ctx):
    # Simulate first sample failing/returning garbage
    mock_ctx.sample.side_effect = ["THIS IS NOT JSON", json.dumps({"achieved": False})]

    with patch("universal_actuator_mcp.server._dispatch_tool", new_callable=AsyncMock) as mock_dispatch:
        mock_dispatch.return_value = {}
        res = await agentic_workflow_tool(goal="Bad plan", ctx=mock_ctx)

        # Should fallback to a basic health check
        assert res["steps_executed"] == 1
        assert res["plan"]["steps"][0]["tool"] == "get_fleet_telemetry"


@pytest.mark.asyncio
async def test_agentic_workflow_step_failure(mock_ctx):
    with patch("universal_actuator_mcp.server._dispatch_tool", side_effect=ValueError("Tool crash")):
        res = await agentic_workflow_tool(goal="Failing tool", ctx=mock_ctx)

        assert res["steps_succeeded"] == 0
        assert res["steps_executed"] == 1
        assert res["steps_taken"][0]["status"] == "failed"
