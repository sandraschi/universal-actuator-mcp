import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("consumption_router.fleet")


class FleetAggregator:
    def __init__(self, config_manager: Any):
        self.config_manager = config_manager
        self.sessions: dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self._lock = asyncio.Lock()

    async def get_session(self, server_name: str) -> ClientSession | None:
        async with self._lock:
            if server_name in self.sessions:
                return self.sessions[server_name]

            server_config = self.config_manager.get_server_config(server_name)
            if not server_config:
                logger.error(f"No config found for server: {server_name}")
                return None

            try:
                params = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    env=server_config.get("env"),
                )

                logger.info(f"Connecting to {server_name}...")
                ctx_stdio = stdio_client(params)
                read, write = await self.exit_stack.enter_async_context(ctx_stdio)
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))

                await session.initialize()
                self.sessions[server_name] = session
                logger.info(f"Successfully connected to {server_name}")
                return session
            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
                return None

    async def close(self):
        """Cleanup all sessions and subprocesses."""
        logger.info("Closing all fleet sessions...")
        await self.exit_stack.aclose()
        self.sessions.clear()

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        session = await self.get_session(server_name)
        if not session:
            raise RuntimeError(f"Could not establish session with {server_name}")

        return await session.call_tool(tool_name, arguments)

    async def list_tools(self, server_name: str) -> list[Any]:
        session = await self.get_session(server_name)
        if not session:
            return []

        result = await session.list_tools()
        return result.tools

    async def aggregate_search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """SOTA Federated Search: Parallel Fan-Out across Media, Docs, and Memory."""
        logger.info(f"Initiating parallel fan-out search for: {query}")
        
        # Define search tasks
        search_tasks = [
            self._search_node("calibre", "search_books", {"query": query, "limit": limit}, self._format_calibre_results),
            self._search_node("plex", "search", {"query": query, "limit": limit}, self._format_plex_results),
            self._search_node("docsops", "search_docs", {"query": query, "limit": limit}, self._format_docs_results),
            self._search_node("knowledge", "search_notes", {"query": query, "results_per_page": limit}, self._format_knowledge_results),
        ]
        
        # Execute concurrently with robust error handling
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Flatten and filter out exceptions
        flattened_results = []
        for res in all_results:
            if isinstance(res, list):
                flattened_results.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"Search task sub-component failed: {res}")
                
        # Sort by source (simple initial grouping)
        return sorted(flattened_results, key=lambda x: x.get("source", ""))

    async def _search_node(self, server_name: str, tool_name: str, args: dict, formatter: Any) -> list[dict[str, Any]]:
        """Helper to search a single node and format results."""
        try:
            res = await self.call_tool(server_name, tool_name, args)
            
            # Extract content from MCP ToolResponse
            if res and hasattr(res, "content") and res.content:
                try:
                    # Most FastMCP tools return a JSON string in the first text content block
                    text_data = res.content[0].text
                    import json
                    data = json.loads(text_data)
                    return formatter(data)
                except (json.JSONDecodeError, AttributeError, IndexError):
                    # Fallback: if it's already a list or dict
                    return formatter(res.content)
            elif isinstance(res, (list, dict)):
                return formatter(res)
            return []
        except Exception as e:
            logger.warning(f"Node search failed for {server_name}: {e}")
            return []

    def _format_calibre_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        if not isinstance(raw_results, list):
            return formatted
        for item in raw_results:
            formatted.append({
                "title": item.get("title", "Unknown Title"),
                "author": item.get("authors", [None])[0],
                "source": "calibre",
                "type": "book",
                "id": str(item.get("id", "")),
                "metadata": {"series": item.get("series"), "tags": item.get("tags", [])}
            })
        return formatted

    def _format_plex_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # Plex sometimes returns the media list directly or inside a 'media' key
        items = raw_results if isinstance(raw_results, list) else raw_results.get("media", []) if isinstance(raw_results, dict) else []
        for item in items:
            formatted.append({
                "title": item.get("title", "Unknown Title"),
                "author": item.get("year"),
                "source": "plex",
                "type": item.get("type", "media"),
                "id": str(item.get("ratingKey", "")),
                "metadata": {"summary": item.get("summary"), "studio": item.get("studio")}
            })
        return formatted

    def _format_docs_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # docsops returns a list of snippets in its 'data' field
        items = raw_results.get("data", []) if isinstance(raw_results, dict) else raw_results
        if not isinstance(items, list):
            return formatted
        for item in items:
            formatted.append({
                "title": item.get("title") or item.get("relative_path", "Documentation"),
                "author": "System",
                "source": "docs",
                "type": "doc",
                "id": item.get("relative_path", ""),
                "metadata": {"snippet": item.get("content", "")[:200], "score": item.get("score")}
            })
        return formatted

    def _format_knowledge_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # knowledge returns a 'results' list
        items = raw_results.get("results", []) if isinstance(raw_results, dict) else raw_results
        if not isinstance(items, list):
            return formatted
        for item in items:
            formatted.append({
                "title": item.get("title", "Note"),
                "author": "Memory",
                "source": "knowledge",
                "type": "note",
                "id": item.get("permalink", ""),
                "metadata": {"tags": item.get("tags", []), "project": item.get("project")}
            })
        return formatted
