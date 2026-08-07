"""
SOTA Fleet Integration Layer — Universal Actuator Hub
Industrial mediation between the Gateway and federated media nodes.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import subprocess
from pathlib import Path
from typing import Any

# Standard relative imports within the package
from .config_manager import ConfigManager
from .fleet_aggregator import FleetAggregator

logger = logging.getLogger("univact.fleet")

# Point to the existing project config in the root
_CONFIG_PATH = str(Path(__file__).parent.parent.parent / "config.json")


# ---------------------------------------------------------------------------
# Config adapter — project config.json uses "servers" not "mcpServers"
# ---------------------------------------------------------------------------


class FleetConfigManager(ConfigManager):
    """Reads project config.json which uses 'servers' key."""

    def get_mcp_servers(self) -> dict[str, Any]:
        return self.config.get("servers", self.config.get("mcpServers", {}))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Helper logic moved to FleetAggregator


# ---------------------------------------------------------------------------
# FleetManager
# ---------------------------------------------------------------------------


class FleetManager:
    """
    PORTMANTEAU PATTERN RATIONALE:
    Orchestrates disparate MCP sessions into a unified, high-availability fleet interface.
    Handles the reduction of federated tool results into standardized media objects.
    """

    def __init__(self) -> None:
        self._cfg_manager = FleetConfigManager(config_path=_CONFIG_PATH)
        self._fleet = FleetAggregator(self._cfg_manager)
        self._processes: dict[str, subprocess.Popen] = {}

    async def close(self) -> None:
        """Industrial shutdown: release all downstream sessions and processes."""
        await self._fleet.close()
        for node_id, proc in self._processes.items():
            if proc.poll() is None:
                logger.info(f"Shutting down headless node: {node_id}")
                proc.terminate()
        self._processes.clear()

    # --- Autostart / Ensure Logic ---

    def is_port_open(self, host: str, port: int) -> bool:
        """Check if a port is bound (indicating the service is alive)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0

    async def ensure_all(self) -> dict[str, str]:
        """
        INDUSTRIAL LOGIC:
        Ensures all federated media nodes are active.
        If a port is closed, triggers a headless backend startup.
        """
        nodes = self._cfg_manager.get_mcp_servers()
        results = {}

        for node_id, config in nodes.items():
            # Only ensure nodes with a defined URL/SSE scheme (the media fleet)
            if "url" not in config or config.get("scheme") != "sse":
                continue

            url = config["url"]
            try:
                host, port_str = url.split(":")
                port = int(port_str)
            except (ValueError, AttributeError):
                logger.warning(f"Invalid URL for node {node_id}: {url}")
                continue

            if self.is_port_open(host, port):
                logger.debug(f"Fleet node '{node_id}' is already active on {url}")
                results[node_id] = "online"
            else:
                logger.info(f"Fleet node '{node_id}' is offline. Triggering headless start...")
                success = await self._start_node_headless(node_id, config, host, port)
                results[node_id] = "starting" if success else "failed"

        return results

    async def _start_node_headless(self, node_id: str, config: dict, host: str, port: int) -> bool:
        """
        Starts an MCP node in the background using 'uv run'.
        Uses environment variables (MCP_TRANSPORT, MCP_PORT) for maximum compatibility.
        """
        python_path = config.get("env", {}).get("PYTHONPATH", "")
        if not python_path:
            logger.error(f"Cannot start {node_id}: No PYTHONPATH found in config.")
            return False

        # Infer repo root from PYTHONPATH (e.g. D:/Dev/repos/plex-mcp/src -> D:/Dev/repos/plex-mcp)
        first_path = python_path.split(";")[0]
        repo_root = str(Path(first_path).parent)

        # Standard industrial command: uv run -m <module>
        module = ""
        args = config.get("args", [])
        if "-m" in args:
            m_idx = args.index("-m")
            if m_idx + 1 < len(args):
                module = args[m_idx + 1]

        if not module:
            logger.error(f"Cannot start {node_id}: module name not found in args.")
            return False

        # Use environment variables for transport. SOTA servers (FastMCP + our wrapper) respect these.
        env = {
            **os.environ,
            "PYTHONPATH": python_path,
            "MCP_TRANSPORT": "http",
            "MCP_PORT": str(port),
            "MCP_HOST": host,
            "PYTHONUNBUFFERED": "1",
        }

        cmd = ["uv", "run", "python", "-m", module]
        logger.info(f"Executing industrial headless start for {node_id} (port {port})")

        try:
            # CREATE_NO_WINDOW (0x08000000) prevents terminal popups on Windows
            creation_flags = 0
            if os.name == "nt":
                creation_flags = 0x08000000

            proc = subprocess.Popen(
                cmd,
                cwd=repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                creationflags=creation_flags,
            )
            self._processes[node_id] = proc

            # Short wait and verify port
            for _ in range(10):
                await asyncio.sleep(1.0)
                if self.is_port_open(host, port):
                    logger.info(f"Fleet node '{node_id}' successfully reached on {host}:{port}")
                    return True
                if proc.poll() is not None:
                    logger.error(f"Fleet node '{node_id}' exited prematurely with code {proc.returncode}")
                    return False

            logger.warning(f"Fleet node '{node_id}' started but port {port} is not yet open.")
            return True
        except Exception as e:
            logger.error(f"Failed to spawn {node_id}: {e}")
            return False

    # --- Calibre ---

    async def search_calibre(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search(query, limit)
        return results.get("calibre", [])

    async def list_calibre(self, limit: int = 500) -> list[dict[str, Any]]:
        """Bulk fetch for RAG ingestion."""
        # aggregator.aggregate_search with empty query generally triggers a fallback list
        results = await self._fleet.aggregate_search("", limit)
        return results.get("calibre", [])

    # --- Plex ---

    async def search_plex(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search(query, limit)
        return results.get("plex", [])

    async def list_plex(self, limit: int = 500) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search("", limit)
        return results.get("plex", [])

    # --- Immich ---

    async def search_immich(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search(query, limit)
        return results.get("immich", [])

    async def list_immich(self, limit: int = 500) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search("", limit)
        return results.get("immich", [])

    # --- Federated ---

    async def search_all(self, query: str, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        """Concurrent federated search across all nodes (Calibre, Plex, Docs, Memory, Immich)."""
        return await self._fleet.aggregate_search(query, limit)

    async def list_docs(self, limit: int = 500) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search("", limit)
        return results.get("docsops", [])  # 'docsops' is the key in sourced_results

    async def list_knowledge(self, limit: int = 500) -> list[dict[str, Any]]:
        results = await self._fleet.aggregate_search("", limit)
        return results.get("knowledge", [])

    async def ingest_all_to_rag(self, rag: Any, limit: int = 500) -> dict[str, int]:
        """
        REDUCTIONIST INGESTION LOGIC:
        Aggregates metadata from all 5 federated nodes in parallel.
        Normalizes results into a flat ingestion stream for the LanceDB index.
        """
        logger.info(f"Industrial Ingest: Fetching from 5 nodes (limit={limit})...")

        # Parallel fetch from all nodes
        results = await asyncio.gather(
            self.list_calibre(limit),
            self.list_plex(limit),
            self.list_immich(limit),
            self.list_docs(limit),
            self.list_knowledge(limit),
            return_exceptions=True,
        )

        sources = ["calibre", "plex", "immich", "docsops", "knowledge"]
        counts: dict[str, int] = {}

        all_items = []
        for source, items in zip(sources, results, strict=False):
            if isinstance(items, list) and items:
                all_items.extend(items)
                counts[source] = len(items)
                logger.info(f"Fleet fetch: {source} → {len(items)} items")
            else:
                counts[source] = 0
                if isinstance(items, Exception):
                    logger.warning(f"Fleet fetch: {source} failed — {items}")
                else:
                    logger.info(f"Fleet fetch: {source} returned no items")

        if all_items:
            # Batch ingest into LanceDB
            n = await rag.ingest_items(all_items)
            logger.info(f"Unified RAG ingest complete: {n} total items indexed.")
            counts["total"] = n
        else:
            counts["total"] = 0

        return counts
