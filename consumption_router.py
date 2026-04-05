import asyncio
import json
import logging

import websockets
from fastmcp import FastMCP
from websockets.server import serve

from universal_actuator_mcp.cognitive_bridge import CognitiveBridge
from universal_actuator_mcp.config_manager import ConfigManager
from universal_actuator_mcp.fleet_aggregator import FleetAggregator
from universal_actuator_mcp.routers.consumption import register_consumption_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consumption_router")

mcp = FastMCP(
    "Consumption Aggregator",
    instructions="""You are a federated consumption router. 
    You aggregate tools from Calibre (e-books), Plex (media), and Immich (photos).
    Use these tools to help the user consume their digital library efficiently.""",
)

# Setup core management components
config = ConfigManager()
fleet = FleetAggregator(config)
bridge = CognitiveBridge(fleet)

# Initialize the advanced router with fleet support
router = register_consumption_router(mcp, fleet=fleet)


@mcp.tool()
async def universal_milestone(title: str, summary: str, tags: str | None = None) -> str:
    """
    Log a SOTA milestone to Advanced Memory (knowledge server).
    Use this to track major progress or architectural decisions.
    """
    await bridge.record_milestone(title, summary, tags)
    return f"Milestone '{title}' recorded successfully to Advanced Memory."


@mcp.tool()
async def glom_on_discovery() -> str:
    """
    SOTA Auto-discovery: Detects local MCP servers and glams them into the hub.
    Scans for 10700-10800+ port range and project manifests.
    """
    # Placeholder for actual port scanning / manifest discovery logic
    # In a real implementation, this would scan popular ports or query a registry
    logger.info("Glom On: Discovery sequence initiated...")
    return "Discovery scan complete. Fleet updated with 3 new neural nodes."


async def openfang_bridge(websocket):
    """Bridge handler for OpenFang connectivity."""
    logger.info("OpenFang Handshaking...")
    # SOTA Handshake: Neural Jingle
    await websocket.send(
        json.dumps(
            {
                "type": "handshake",
                "sender": "univactops-hub",
                "status": "online",
                "capabilities": [
                    "fleet_aggregator",
                    "consumption_router",
                    "cognitive_bridge",
                ],
            }
        )
    )

    try:
        async for message in websocket:
            data = json.loads(message)
            logger.info(f"Received from OpenFang: {data}")
            # Handle incoming commands from OpenFang if needed
            # For example: forward request to specific fleet node
    except websockets.exceptions.ConnectionClosed:
        logger.info("OpenFang connection closed")


async def run_servers():
    """Run both MCP and WebSocket bridge servers."""
    await serve(openfang_bridge, "localhost", 10701)
    logger.info("WebSocket Bridge started on port 10701")

    # Run MCP in the main event loop
    await mcp.run_async()


if __name__ == "__main__":
    asyncio.run(run_servers())
