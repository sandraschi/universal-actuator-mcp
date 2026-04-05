import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger("consumption_router.core")


class MediaItem(BaseModel):
    title: str
    author: str | None = None
    source: str  # "calibre" or "plex"
    type: str  # "book", "movie", "show", etc.
    id: str
    metadata: dict = Field(default_factory=dict)


def register_consumption_router(mcp: FastMCP, fleet: Any) -> FastMCP:
    """Registers unified consumption tools (search, details) to the main MCP."""

    @mcp.tool()
    async def search_library(query: str, limit: int = 10) -> list[MediaItem]:
        """Unified search across Calibre and Plex libraries."""
        logger.info(f"Hub Search: {query}")
        return await fleet.aggregate_search(query, limit)

    @mcp.tool()
    async def get_recommendations(topic: str) -> list[MediaItem]:
        """
        Get cross-platform recommendations based on a topic.
        """
        # Implementation for intelligent recommendations
        return []

    return mcp
