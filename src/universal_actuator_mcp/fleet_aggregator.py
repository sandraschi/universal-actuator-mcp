import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

logger = logging.getLogger("univact.media_aggregator")


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
                scheme = server_config.get("scheme", "stdio").lower()

                if scheme == "sse":
                    url = server_config.get("url")
                    if not url:
                        logger.error(f"SSE scheme specified for {server_name} but no url found")
                        return None

                    # Ensure full URL with /sse endpoint
                    full_url = url if url.startswith("http") else f"http://{url}"
                    if not full_url.endswith("/sse"):
                        full_url = full_url.rstrip("/") + "/sse"

                    logger.info(f"Connecting to {server_name} via SSE at {full_url}...")
                    ctx_sse = sse_client(url=full_url)
                    read, write = await self.exit_stack.enter_async_context(ctx_sse)
                    session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                else:
                    # Stdio fallback (Subprocess)
                    params = StdioServerParameters(
                        command=server_config["command"],
                        args=server_config.get("args", []),
                        env=server_config.get("env"),
                    )

                    logger.info(f"Connecting to {server_name} via Stdio (Subprocess)...")
                    ctx_stdio = stdio_client(params)
                    read, write = await self.exit_stack.enter_async_context(ctx_stdio)
                    session = await self.exit_stack.enter_async_context(ClientSession(read, write))

                # Initialize session with timeout
                try:
                    await asyncio.wait_for(session.initialize(), timeout=15)
                    self.sessions[server_name] = session
                    logger.info(f"Successfully connected to {server_name}")
                    return session
                except TimeoutError:
                    logger.error(f"Initialization timeout for {server_name}")
                    return None
            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
                return None

    async def close(self):
        """Cleanup all sessions and subprocesses."""
        logger.info("Closing all fleet sessions...")
        await self.exit_stack.aclose()
        self.sessions.clear()

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any], timeout: int = 10) -> Any:
        session = await self.get_session(server_name)
        if not session:
            raise RuntimeError(f"Could not establish session with {server_name}")

        try:
            return await asyncio.wait_for(session.call_tool(tool_name, arguments), timeout=timeout)
        except TimeoutError:
            logger.error(f"Tool call to {server_name}:{tool_name} timed out after {timeout}s")
            raise

    async def list_tools(self, server_name: str) -> list[Any]:
        session = await self.get_session(server_name)
        if not session:
            return []

        result = await session.list_tools()
        return result.tools

    async def aggregate_search(self, query: str, limit: int = 10) -> dict[str, list[dict[str, Any]]]:
        """SOTA Federated Search: Parallel Fan-Out across Media, Docs, and Memory."""
        logger.info(f"Initiating parallel fan-out search for: {query}")

        # Define search tasks with real portmanteau signatures
        # For empty queries, we switch to listing/recent operations where possible
        is_list = not query.strip()

        search_tasks = [
            self._search_node(
                "calibre",
                "query_books",
                {"operation": "recent" if is_list else "search", "query": query, "limit": limit},
                self._format_calibre_results,
            ),
            self._search_node(
                "plex",
                "plex_search",
                {"query": query if query else " ", "limit": limit},  # Plex search often requires a char
                self._format_plex_results,
            ),
            self._search_node(
                "docsops",
                "search_docs",
                {"query": query if query else "overview", "limit": limit},  # Fallback to overview for list
                self._format_docs_results,
            ),
            self._search_node(
                "knowledge",
                "adn_knowledge",
                {"operation": "search", "query": query if query else " ", "page": 1, "results_per_page": limit},
                self._format_knowledge_results,
            ),
            self._search_node(
                "immich",
                "search_photos",
                {"query": query if query else " ", "limit": limit},
                self._format_immich_results,
            ),
        ]

        # Execute concurrently with robust error handling
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Map results back to their respective sources
        sourced_results = {"calibre": [], "plex": [], "docsops": [], "knowledge": [], "immich": []}

        for res in all_results:
            if isinstance(res, list) and res:
                src_key = res[0].get("source")
                if src_key in sourced_results:
                    # Append instead of replace if multiple formatters return same source
                    sourced_results[src_key].extend(res)
                else:
                    # Fallback for unexpected or newly glommed sources
                    sourced_results[res[0].get("source", "unknown")] = res
            elif isinstance(res, Exception):
                logger.error(f"Search task sub-component failed: {res}")

        return sourced_results

    async def _search_node(self, server_name: str, tool_name: str, args: dict, formatter: Any) -> list[dict[str, Any]]:
        """Helper to search a single node and format results."""
        try:
            res = await self.call_tool(server_name, tool_name, args)

            # Extract content from MCP ToolResponse (FastMCP Standard)
            data = None
            if hasattr(res, "content") and res.content:
                # Iterate through content to find text blocks
                for block in res.content:
                    # Generic FastMCP content block extraction
                    text_val = None
                    if hasattr(block, "text"):
                        text_val = block.text
                    elif isinstance(block, dict) and "text" in block:
                        text_val = block["text"]

                    if text_val:
                        try:
                            import json

                            # Attempt to parse json if it looks like a list/dict serialized
                            parsed = json.loads(text_val)
                            if isinstance(parsed, (list, dict)):
                                data = parsed
                                break
                        except Exception:
                            # If not JSON, but we have text, we might want to wrap it
                            data = text_val

            # Fallback if no JSON/text extracted from content blocks
            if data is None:
                # Handle direct response if it's already a dict/list (mocked servers)
                if isinstance(res, (list, dict)):
                    data = res
                elif hasattr(res, "dict"):  # Pydantic fallback
                    data = res.dict()
                else:
                    data = []

            return formatter(data)
        except Exception as e:
            logger.warning(f"Node search failed for {server_name}: {e}")
            return []

    def _format_calibre_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # Calibre often returns result in a 'result' key or a list
        items = (
            raw_results
            if isinstance(raw_results, list)
            else raw_results.get("result", [])
            if isinstance(raw_results, dict)
            else []
        )
        if not items and isinstance(raw_results, dict) and "items" in raw_results:
            items = raw_results["items"]

        for item in items:
            formatted.append(
                {
                    "title": item.get("title", "Unknown Title"),
                    "author": item.get("authors", [None])[0] if item.get("authors") else "Unknown",
                    "source": "calibre",
                    "type": "book",
                    "id": str(item.get("id", "")),
                    "metadata": {
                        "series": item.get("series"),
                        "tags": item.get("tags", []),
                        "rating": item.get("rating"),
                    },
                }
            )
        return formatted

    def _format_plex_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # Plex sometimes returns the media list directly or inside a 'media' key
        items = (
            raw_results
            if isinstance(raw_results, list)
            else raw_results.get("media", [])
            if isinstance(raw_results, dict)
            else []
        )
        for item in items:
            formatted.append(
                {
                    "title": item.get("title", "Unknown Title"),
                    "author": str(item.get("year", "N/A")),
                    "source": "plex",
                    "type": "movie"
                    if item.get("type") == "movie"
                    else "show"
                    if item.get("type") == "show"
                    else "media",
                    "id": str(item.get("ratingKey", "")),
                    "metadata": {
                        "summary": item.get("summary"),
                        "studio": item.get("studio"),
                        "rating": item.get("rating"),
                    },
                }
            )
        return formatted

    def _format_docs_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # docsops returns a list of snippets in its 'data' field
        items = raw_results.get("data", []) if isinstance(raw_results, dict) else raw_results
        if not isinstance(items, list):
            return formatted
        for item in items:
            formatted.append(
                {
                    "title": item.get("title") or item.get("relative_path", "Documentation"),
                    "author": "System",
                    "source": "docsops",
                    "type": "doc",
                    "id": item.get("relative_path", ""),
                    "metadata": {"snippet": item.get("content", "")[:200], "score": item.get("score")},
                }
            )
        return formatted

    def _format_knowledge_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        # knowledge returns a 'results' list or direct list
        items = raw_results.get("results", []) if isinstance(raw_results, dict) else raw_results
        if not isinstance(items, list):
            # check data field
            items = raw_results.get("data", []) if isinstance(raw_results, dict) else []

        if not isinstance(items, list):
            return formatted

        for item in items:
            formatted.append(
                {
                    "title": item.get("title", item.get("headline", "Note")),
                    "author": "Memory",
                    "source": "knowledge",
                    "type": "note",
                    "id": item.get("permalink", item.get("id", "")),
                    "metadata": {"tags": item.get("tags", []), "project": item.get("project")},
                }
            )
        return formatted

    def _format_immich_results(self, raw_results: Any) -> list[dict[str, Any]]:
        formatted = []
        items = raw_results if isinstance(raw_results, list) else []
        for item in items:
            formatted.append(
                {
                    "title": item.get("original_filename", "Photo"),
                    "author": item.get("created_at"),
                    "source": "immich",
                    "type": "photo",
                    "id": str(item.get("id", "")),
                    "metadata": {"path": item.get("file_path"), "score": item.get("smart_search_score")},
                }
            )
        return formatted
