"""
Universal Actuator MCP prompt templates (FastMCP ``@mcp.prompt``).

PORTMANTEAU PATTERN RATIONALE: Prompts are discoverable, reusable instruction blocks
that clients inject into the conversation; they complement the portmanteau tools and
the bundled ``skill://universal-actuator`` skill without duplicating tool schemas.
"""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all ``@mcp.prompt`` handlers on the given FastMCP instance."""

    @mcp.prompt()
    def federated_search_brief() -> str:
        """Start a federated search across the fleet: what to ask, which domain, how to read hits."""
        return """Run a federated search across the fleet. First call universal_status() to see which
domains are online, then search_federated(query="...", domain="...") with the narrowest domain
that fits (calibre for books, plex for media, immich for photos, docs/knowledge for notes,
all only when unsure). Report per-source hit counts, then the top 5 results with source labels."""

    @mcp.prompt()
    def milestone_review() -> str:
        """Review what the fleet accomplished: milestone timeline plus RAG/telemetry context."""
        return """Review fleet accomplishments. Call get_milestones_history() for the timeline,
rag_stats() for index size, and get_fleet_telemetry() for live health. Summarise what was
achieved, what is stale (milestones older than 7 days with no follow-up), and suggest the
next milestone to record via universal_milestone(title=..., description=...)."""

    @mcp.prompt()
    def telemetry_triage() -> str:
        """Triage a sick fleet: telemetry first, then glom_on, then targeted discovery."""
        return """Triage fleet health. Call get_fleet_telemetry() first: if active_nodes is 0, run
glom_on() to re-scan configs and ports 10700-10900. For each offline node, check whether its
backend process is a zombie (port open, no response) or truly down, and report which nodes
need `start.ps1` restarts. Never restart nodes you were not asked to touch."""
