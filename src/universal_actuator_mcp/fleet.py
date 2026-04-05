"""
Fleet integration layer for the Universal Actuator backend server.

Bridges backend/server.py to FleetAggregator + individual downstream MCP servers
(Calibre, Plex, Immich). Handles:
  - FleetConfigManager: reads 'servers' key from project config.json
  - FleetManager: high-level search + bulk-list methods used by the backend
"""
from __future__ import annotations

import asyncio
import json
import logging
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

def _extract_json(result: Any) -> Any:
    """Unpack MCP CallToolResult → Python object."""
    if result is None:
        return None
    # FastMCP returns objects with .content list of TextContent
    if hasattr(result, "content") and result.content:
        text = result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text
    if isinstance(result, (dict, list)):
        return result
    try:
        return json.loads(str(result))
    except (json.JSONDecodeError, TypeError):
        return result


def _fmt_immich(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for item in items:
        out.append({
            "title": item.get("originalFileName") or item.get("albumName") or item.get("name") or "Unknown",
            "author": item.get("ownerId"),
            "source": "immich",
            "type": item.get("type", "photo").lower(),
            "id": str(item.get("id", item.get("assetId", ""))),
            "metadata": {
                "created": item.get("fileCreatedAt"),
                "city": item.get("exifInfo", {}).get("city") if isinstance(item.get("exifInfo"), dict) else None,
                "album": item.get("albumName"),
            },
        })
    return out


# ---------------------------------------------------------------------------
# FleetManager
# ---------------------------------------------------------------------------

class FleetManager:
    """
    High-level fleet operations for the backend server.

    Usage (in lifespan):
        fleet = FleetManager()
        # no explicit init needed — FleetAggregator connects lazily
        ...
        await fleet.close()
    """

    def __init__(self) -> None:
        cfg = FleetConfigManager(config_path=_CONFIG_PATH)
        self._fleet = FleetAggregator(cfg)

    async def close(self) -> None:
        await self._fleet.close()

    # --- Calibre ---

    async def search_calibre(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        try:
            result = await self._fleet.call_tool("calibre", "search_books", {"query": query, "limit": limit})
            raw = _extract_json(result)
            return self._fleet._format_calibre_results(raw) if isinstance(raw, list) else []
        except Exception as e:
            logger.warning(f"Calibre search_books failed: {e}")
            return []

    async def list_calibre(self, limit: int = 500) -> list[dict[str, Any]]:
        """Bulk fetch for RAG ingestion."""
        # Try list_books first, fallback to search with wildcard
        for tool, args in [
            ("list_books", {"limit": limit}),
            ("search_books", {"query": "", "limit": limit}),
            ("search_books", {"query": "*", "limit": limit}),
        ]:
            try:
                result = await self._fleet.call_tool("calibre", tool, args)
                raw = _extract_json(result)
                if isinstance(raw, list) and raw:
                    return self._fleet._format_calibre_results(raw)
            except Exception as e:
                logger.debug(f"Calibre {tool} failed: {e}")
        logger.warning("All Calibre list attempts failed.")
        return []

    # --- Plex ---

    async def search_plex(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        try:
            result = await self._fleet.call_tool("plex", "search", {"query": query, "limit": limit})
            raw = _extract_json(result)
            return self._fleet._format_plex_results(raw) if isinstance(raw, list) else []
        except Exception as e:
            logger.warning(f"Plex search failed: {e}")
            return []

    async def list_plex(self, limit: int = 500) -> list[dict[str, Any]]:
        """Bulk fetch for RAG ingestion — try several plausible tool names."""
        items: list[dict[str, Any]] = []
        for tool, args in [
            ("get_all_media", {"limit": limit}),
            ("list_media", {"limit": limit}),
            ("get_libraries", {}),
            ("search", {"query": "", "limit": limit}),
        ]:
            try:
                result = await self._fleet.call_tool("plex", tool, args)
                raw = _extract_json(result)
                if isinstance(raw, list) and raw:
                    items = self._fleet._format_plex_results(raw)
                    break
            except Exception as e:
                logger.debug(f"Plex {tool} failed: {e}")
        return items[:limit]

    # --- Immich ---

    async def search_immich(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        for tool, args in [
            ("search_assets", {"query": query, "limit": limit}),
            ("search_photos", {"query": query, "limit": limit}),
            ("search", {"query": query, "limit": limit}),
        ]:
            try:
                result = await self._fleet.call_tool("immich", tool, args)
                raw = _extract_json(result)
                if isinstance(raw, list):
                    return _fmt_immich(raw)
            except Exception as e:
                logger.debug(f"Immich {tool} failed: {e}")
        logger.warning("All Immich search attempts failed.")
        return []

    async def list_immich(self, limit: int = 500) -> list[dict[str, Any]]:
        """Bulk fetch for RAG ingestion."""
        for tool, args in [
            ("list_albums", {"limit": limit}),
            ("list_assets", {"limit": limit}),
            ("get_assets", {"limit": limit}),
            ("search_assets", {"query": "", "limit": limit}),
        ]:
            try:
                result = await self._fleet.call_tool("immich", tool, args)
                raw = _extract_json(result)
                if isinstance(raw, list) and raw:
                    return _fmt_immich(raw)[:limit]
            except Exception as e:
                logger.debug(f"Immich {tool} failed: {e}")
        return []

    # --- Federated ---

    async def search_all(self, query: str, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        """Concurrent federated search across Calibre, Plex, Immich."""
        # Use the parallel aggregator directly for maximum efficiency
        return await self._fleet.aggregate_search(query, limit)

    async def ingest_all_to_rag(self, rag: Any, limit: int = 500) -> dict[str, int]:
        """
        Bulk-list all sources and ingest into the provided LanceDBRag instance.
        Returns per-source ingest counts.
        """
        calibre_items, plex_items, immich_items = await asyncio.gather(
            self.list_calibre(limit),
            self.list_plex(limit),
            self.list_immich(limit),
            return_exceptions=True,
        )

        counts: dict[str, int] = {}
        for source, items in [("calibre", calibre_items), ("plex", plex_items), ("immich", immich_items)]:
            if isinstance(items, list) and items:
                n = await rag.ingest_items(items)
                counts[source] = n
                logger.info(f"Fleet RAG ingest: {source} → {n} items")
            else:
                counts[source] = 0
                if isinstance(items, Exception):
                    logger.warning(f"Fleet RAG ingest: {source} failed — {items}")

        return counts
