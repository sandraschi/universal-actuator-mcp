import logging

from .fleet_aggregator import FleetAggregator

logger = logging.getLogger("consumption_router.bridge")


class CognitiveBridge:
    """
    SOTA Cognitive Bridge connecting the Universal Actuator to Advanced Memory.
    Enables semantic context retrieval and milestone tracking.
    """

    def __init__(self, fleet: FleetAggregator):
        self.fleet = fleet

    async def get_semantic_context(self, query: str, limit: int = 5) -> str:
        """Retrieves semantic context from Advanced Memory using RAG."""
        try:
            # Using the 'knowledge' server defined in config.json
            result = await self.fleet.call_tool("knowledge", "adn_knowledge_rag", {"query": query, "limit": limit})

            if isinstance(result, dict) and "high_density_summary" in result:
                return result["high_density_summary"]
            return str(result)
        except Exception as e:
            logger.warning(f"Cognitive Bridge: Context retrieval failed (is 'knowledge' server running?): {e}")
            return "Context unavailable."

    async def record_milestone(self, title: str, summary: str, tags: str | None = None):
        """Records an industrial-grade milestone to Advanced Memory."""
        try:
            content = f"## Milestone: {title}\n\n{summary}\n\n---\n*Logged via Universal Actuator Cognitive Bridge*"
            actual_tags = tags if tags else "#milestone, #universal-actuator, #empirical-verification"

            await self.fleet.call_tool(
                "knowledge",
                "adn_knowledge",
                {
                    "operation": "create",
                    "title": title,
                    "content": content,
                    "folder": "milestones/actuator",
                    "tags": actual_tags,
                },
            )
            logger.info(f"Milestone recorded: {title}")
        except Exception as e:
            logger.error(f"Cognitive Bridge: Failed to record milestone '{title}': {e}")
