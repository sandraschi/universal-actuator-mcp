import logging
from typing import Annotated, Any

from fastmcp import FastMCP
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
    async def search_library(
        query: Annotated[str, Field(description="Search query across Calibre and Plex libraries.")],
        limit: Annotated[int, Field(description="Max results.", ge=1, le=50)] = 10,
    ) -> list[MediaItem]:
        """
        Unified search across Calibre and Plex libraries.

        NOTE: register_media_router() is currently not wired into server.py -
        search_federated() is the live equivalent. Wiring is deferred, not silent.

        ## Return Format
        [MediaItem, ...] with title/author/source/type/id/metadata.

        ## Examples
        - search_library(query="dune", limit=5)
        """
        logger.info(f"Media Search: {query}")
        return await fleet.aggregate_search(query, limit)

    @mcp.tool()
    async def get_recommendations(
        topic: Annotated[str | None, Field(description="Optional topic.")] = None,
    ) -> list[MediaItem]:
        """
        Get cross-platform recommendations. Topic is optional.

        NOTE: register_media_router() is currently not wired into server.py -
        search_federated() is the live equivalent. Wiring is deferred, not silent.

        ## Return Format
        [MediaItem, ...] with title/author/source/type/id/metadata.

        ## Examples
        - get_recommendations(topic="space opera")
        """
        query = topic if topic else "featured"
        logger.info(f"Media Recommendations for: {query}")
        # Real implementation: we search for the topic or 'featured' items across the grid
        return await fleet.aggregate_search(query, limit=5)

    return mcp
