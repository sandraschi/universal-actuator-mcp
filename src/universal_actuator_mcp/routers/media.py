import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger("univact.media_router")


class MediaItem(BaseModel):
    title: str
    author: str | None = None
    source: str  # "calibre", "plex", etc.
    type: str  # "book", "movie", "show", etc.
    id: str
    metadata: dict = Field(default_factory=dict)


def register_media_router(mcp: FastMCP, fleet: Any) -> FastMCP:
    """Registers unified media discovery tools to the main MCP."""

    @mcp.tool()
    async def search_library(query: str, limit: int = 10) -> list[MediaItem]:
        """Unified search across Calibre and Plex libraries."""
        logger.info(f"Media Search: {query}")
        return await fleet.aggregate_search(query, limit)

    @mcp.tool()
    async def get_recommendations(topic: str | None = None) -> list[MediaItem]:
        """
        Get cross-platform recommendations. Topic is optional.
        """
        query = topic if topic else "featured"
        logger.info(f"Media Recommendations for: {query}")
        # Real implementation: we search for the topic or 'featured' items across the grid
        return await fleet.aggregate_search(query, limit=5)

    return mcp
