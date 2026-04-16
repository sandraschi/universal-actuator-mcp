import asyncio
import json
import logging

import aiohttp
import uvicorn
import websockets
from fastmcp import Context, FastMCP
from starlette.middleware.cors import CORSMiddleware
from websockets.server import serve

from universal_actuator_mcp.cognitive_bridge import CognitiveBridge
from universal_actuator_mcp.config_manager import ConfigManager
from universal_actuator_mcp.fleet_aggregator import FleetAggregator
from universal_actuator_mcp.routers.media import register_media_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("univact.media_hub")

mcp = FastMCP(
    "Media Hub Aggregator",
    instructions="""You are a federated Media Hub.
    You aggregate tools from Calibre (e-books), Plex (media), and Immich (photos).
    Use these tools to help the user search, discover, and consume their digital library efficiently.""",
)

# Enable CORS for industrial SOTA frontend
app = mcp.http_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup core management components
config = ConfigManager()
fleet = FleetAggregator(config)
bridge = CognitiveBridge(fleet)

# Initialize the advanced router with fleet support
router = register_media_router(mcp, fleet=fleet)


@mcp.tool()
async def list_ollama_models(ctx: Context) -> list[str]:
    """Elicit available LLM models from the local Ollama instance (no hardcoding)."""
    url = "http://127.0.0.1:11434/api/tags"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2.0) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return models if models else ["llama3", "mistral"]
                return ["llama3", "mistral"]
    except Exception:
        return ["llama3", "mistral"]


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
    SOTA Auto-discovery: Scans local ports 10700-10800 for active MCP nodes.
    Automatically identifies and glams new neural nodes into the hub.
    """
    logger.info("Glom On: Starting SOTA Port Scan (10700-10800)...")
    discovered_ports = []

    async def probe_port(session, port):
        url = f"http://localhost:{port}/health"
        try:
            async with session.get(url, timeout=0.5) as response:
                if response.status == 200:
                    return port
        except Exception:
            return None

    async with aiohttp.ClientSession() as session:
        tasks = [probe_port(session, port) for port in range(10700, 10801)]
        results = await asyncio.gather(*tasks)
        discovered_ports = [p for p in results if p is not None]

    if not discovered_ports:
        return "Scan complete. No new standalone HTTP MCP nodes detected in target range."

    discovered_str = ", ".join(map(str, discovered_ports))
    msg = f"Scan complete. Discovered {len(discovered_ports)} active nodes on ports: {discovered_str}."
    logger.info(msg)
    return msg


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
                    "media_hub",
                    "cognitive_bridge",
                ],
            }
        )
    )

    try:
        async for message in websocket:
            data = json.loads(message)
            logger.info(f"Received from OpenFang: {data}")
    except websockets.exceptions.ConnectionClosed:
        logger.info("OpenFang connection closed")


async def run_servers():
    """Run both FastMCP (SSE) and WebSocket bridge servers concurrently."""
    # 1. Start WebSocket Bridge for OpenFang
    await serve(openfang_bridge, "localhost", 10746)
    logger.info("WebSocket Bridge started on port 10746")

    # 2. Configure Uvicorn for FastMCP's HTTP/SSE layer
    # We use mcp.http_app() which was already configured with CORS
    config = uvicorn.Config(mcp.http_app(), host="127.0.0.1", port=10747, log_level="info", loop="asyncio")
    mcp_server = uvicorn.Server(config)

    logger.info("Media Hub SSE Server (MCP) starting on port 10747...")
    await mcp_server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        logger.info("Media Hub shutting down...")
