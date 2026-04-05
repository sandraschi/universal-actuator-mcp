"""
Universal Actuator MCP Hub — SOTA Backend Server
FastMCP 3.1 | LanceDB RAG | ctx.sample() Sampling | SEP-1577 Agentic Workflow
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
from fastmcp import Context, FastMCP
from starlette.responses import JSONResponse

# Standard relative imports within the package
from .fleet import FleetManager
from .rag import LanceDBRag

logger = logging.getLogger("UnivActHub")
logging.basicConfig(level=logging.INFO)

# Point to the existing state directory in the root
STATE_DIR = Path(__file__).parent.parent.parent / "backend" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
MILESTONES_FILE = STATE_DIR / "milestones.json"

_rag: LanceDBRag = LanceDBRag()
_fleet: FleetManager | None = None


# Initialize FastMCP 3.1 (name and version only)
mcp = FastMCP(
    "Universal Actuator Hub",
    version="2.0.0",
)


@mcp.lifespan()
async def lifespan(server: FastMCP):
    global _fleet
    logger.info("Universal Actuator Federation Gateway starting (FastMCP 3.1)...")
    await _rag.initialize()
    logger.info("LanceDB RAG initialized.")
    _fleet = FleetManager()
    logger.info("FleetManager ready (Federation Gateway initialized).")
    yield
    logger.info("Shutting down...")
    if _fleet:
        await _fleet.close()
    logger.info("Fleet sessions closed.")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_milestones() -> list[dict[str, Any]]:
    if not MILESTONES_FILE.exists():
        return []
    try:
        return json.loads(MILESTONES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_milestone_internal(title: str, description: str, kind: str = "info") -> dict[str, Any]:
    milestones = _load_milestones()
    entry = {"title": title, "description": description, "type": kind, "timestamp": datetime.now().isoformat()}
    milestones.append(entry)
    MILESTONES_FILE.write_text(json.dumps(milestones, indent=2), encoding="utf-8")
    return entry


async def _scan_port(port: int) -> int | None:
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", port), timeout=0.1)
        writer.close()
        await writer.wait_closed()
        return port
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return None


async def _glom_on_internal() -> dict[str, Any]:
    config_paths = [
        Path(os.environ.get("USERPROFILE", "")) / ".gemini" / "antigravity" / "mcp_config.json",
        Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json",
        Path(os.environ.get("APPDATA", "")) / "Windsurf" / "mcp_config.json",
    ]
    discovered: list[dict[str, Any]] = []
    for path in config_paths:
        if path.exists():
            try:
                config = json.loads(path.read_text(encoding="utf-8"))
                servers_key = "mcpServers" if "mcpServers" in config else "servers"
                for name, details in config.get(servers_key, {}).items():
                    discovered.append({"name": name, "source": str(path), "command": details.get("command"), "active": False})
            except Exception as e:
                logger.error(f"Could not read {path}: {e}")

    tasks = [_scan_port(p) for p in range(10700, 10901)]
    active_ports = [p for p in await asyncio.gather(*tasks) if p is not None]

    for port in active_ports:
        matched = any(d for d in discovered if str(port) in str(d.get("command", "")))
        if not matched:
            discovered.append({"name": f"UnknownService@{port}", "source": "PortScan", "port": port, "active": True})
        else:
            for d in discovered:
                if str(port) in str(d.get("command", "")):
                    d["active"] = True
                    d["port"] = port

    return {
        "discovered_servers": discovered,
        "count": len(discovered),
        "active_count": len(active_ports),
        "active_ports": active_ports,
        "scan_range": "10700-10900",
        "timestamp": datetime.now().isoformat(),
    }


async def _get_fleet_telemetry_internal() -> dict[str, Any]:
    discovery = await _glom_on_internal()
    active_nodes = [n for n in discovery["discovered_servers"] if n.get("active")]
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    return {
        "fleet_status": "Healthy" if active_nodes else "Standalone",
        "active_nodes": len(active_nodes),
        "total_discovered": len(discovery["discovered_servers"]),
        "host_metrics": {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "available_gb": round(mem.available / (1024 ** 3), 2),
        },
        "nodes": [n["name"] for n in active_nodes],
        "telemetry_timestamp": datetime.now().isoformat(),
    }


async def _search_federated_internal(query: str, domain: str = "all") -> dict[str, Any]:
    """Real federated search via FleetManager → Calibre/Plex/Immich MCP servers."""
    assert _fleet is not None, "FleetManager not initialized"
    if domain == "all":
        results = await _fleet.search_all(query)
    elif domain == "calibre":
        results = {"calibre": await _fleet.search_calibre(query), "plex": [], "immich": []}
    elif domain == "plex":
        results = {"calibre": [], "plex": await _fleet.search_plex(query), "immich": []}
    elif domain == "immich":
        results = {"calibre": [], "plex": [], "immich": await _fleet.search_immich(query)}
    else:
        results = await _fleet.search_all(query)

    total = sum(len(v) for v in results.values())
    return {
        "query": query,
        "domain": domain,
        "results": results,
        "total_hits": total,
        "timestamp": datetime.now().isoformat(),
    }


async def _ingest_fleet_to_rag_internal() -> dict[str, Any]:
    """Real bulk ingest from all fleet sources into LanceDB RAG."""
    assert _fleet is not None, "FleetManager not initialized"
    counts = await _fleet.ingest_all_to_rag(_rag, limit=500)
    stats = await _rag.stats()
    return {
        "ingested_per_source": counts,
        "total_ingested": sum(counts.values()),
        "rag_stats": stats,
        "timestamp": datetime.now().isoformat(),
    }


async def _dispatch_tool(tool_name: str, args: dict[str, Any]) -> Any:
    dispatch: dict[str, Any] = {
        "search_federated": lambda: _search_federated_internal(args.get("query", ""), args.get("domain", "all")),
        "rag_semantic_search": lambda: _rag.semantic_search(args.get("query", ""), args.get("limit", 10), args.get("source")),
        "ingest_fleet_to_rag": _ingest_fleet_to_rag_internal,
        "glom_on": _glom_on_internal,
        "get_fleet_telemetry": _get_fleet_telemetry_internal,
        "rag_stats": _rag.stats,
        "rag_clear": _rag.clear,
        "universal_milestone": lambda: _save_milestone_internal(args.get("title", ""), args.get("description", ""), args.get("type", "info")),
        "get_milestones_history": lambda: {"milestones": _load_milestones(), "count": len(_load_milestones())},
    }
    fn = dispatch.get(tool_name)
    if fn is None:
        raise ValueError(f"Unknown tool: '{tool_name}'. Available: {sorted(dispatch)}")
    return await fn()


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_federated(query: str, ctx: Context, domain: str = "all") -> dict[str, Any]:
    """
    Unified search across Plex, Calibre, and Immich via their MCP servers.

    Args:
        query: Search query string.
        domain: "plex", "calibre", "immich", or "all". Default: "all".

    Returns:
        dict with results per source and total_hits.
    """
    await ctx.info(f"[{ctx.correlation_id}] search_federated query={query!r} domain={domain}")
    return await _search_federated_internal(query, domain)


@mcp.tool()
async def rag_semantic_search(query: str, ctx: Context, limit: int = 10, source: str | None = None) -> dict[str, Any]:
    """
    Semantic vector search over the LanceDB media index.

    Call ingest_fleet_to_rag() first to populate. Uses sentence-transformers
    (all-MiniLM-L6-v2) or hash fallback.

    Args:
        query: Natural language query.
        limit: Max results. Default: 10.
        source: Optional filter — "calibre", "plex", or "immich".

    Returns:
        Ranked results with _score (lower = more similar).
    """
    await ctx.info(f"[{ctx.correlation_id}] rag_semantic_search query={query!r} limit={limit} source={source}")
    results = await _rag.semantic_search(query, limit, source)
    stats = await _rag.stats()
    return {
        "query": query,
        "source_filter": source,
        "results": results,
        "result_count": len(results),
        "index_size": stats.get("total_items", 0),
        "embedding_model": stats.get("embedding_model", "unknown"),
    }


@mcp.tool()
async def ingest_fleet_to_rag(ctx: Context) -> dict[str, Any]:
    """
    Bulk-ingest metadata from Calibre, Plex, and Immich into the LanceDB RAG index.

    Fetches up to 500 items per source. Safe to call repeatedly — existing items
    are overwritten by id.

    Returns:
        ingested_per_source, total_ingested, rag_stats.
    """
    await ctx.info(f"[{ctx.correlation_id}] ingest_fleet_to_rag: starting bulk ingest...")
    result = await _ingest_fleet_to_rag_internal()
    await ctx.info(f"[{ctx.correlation_id}] ingest_fleet_to_rag: {result['total_ingested']} items total.")
    return result


@mcp.tool()
async def rag_stats(ctx: Context) -> dict[str, Any]:
    """Return LanceDB RAG index statistics: total_items, embedding_model, source_distribution."""
    await ctx.info(f"[{ctx.correlation_id}] rag_stats")
    return await _rag.stats()


@mcp.tool()
async def rag_clear(ctx: Context) -> dict[str, Any]:
    """Clear the LanceDB RAG index entirely. Use before a fresh ingest."""
    await ctx.warning(f"[{ctx.correlation_id}] rag_clear: dropping index")
    await _rag.clear()
    return {"status": "cleared", "timestamp": datetime.now().isoformat()}


@mcp.tool()
async def glom_on(ctx: Context) -> dict[str, Any]:
    """
    Auto-discovery: scan MCP config files and port range 10700-10900 for active services.

    Returns:
        discovered_servers list, count, active_count, active_ports.
    """
    await ctx.info(f"[{ctx.correlation_id}] glom_on: scanning configs + ports 10700-10900...")
    result = await _glom_on_internal()
    await ctx.info(f"[{ctx.correlation_id}] glom_on: {result['count']} discovered, {result['active_count']} active.")
    return result


@mcp.tool()
async def get_fleet_telemetry(ctx: Context) -> dict[str, Any]:
    """
    Real-time host health + fleet node count (CPU, RAM, active services).

    Returns:
        fleet_status, host_metrics, active_nodes, nodes list.
    """
    await ctx.info(f"[{ctx.correlation_id}] get_fleet_telemetry")
    return await _get_fleet_telemetry_internal()


@mcp.tool()
async def universal_milestone(title: str, description: str, ctx: Context, kind: str = "info") -> dict[str, Any]:
    """
    Log a persistent milestone to the state file.

    Args:
        title: Milestone title.
        description: Description.
        kind: "info", "warning", or "achievement". Default: "info".
    """
    await ctx.info(f"[{ctx.correlation_id}] milestone: {title}")
    return {"status": "recorded", "milestone": _save_milestone_internal(title, description, kind)}


@mcp.tool()
async def get_milestones_history(ctx: Context) -> dict[str, Any]:
    """Retrieve all recorded milestones."""
    await ctx.info(f"[{ctx.correlation_id}] get_milestones_history")
    milestones = _load_milestones()
    return {"milestones": milestones, "count": len(milestones)}


@mcp.tool()
async def agentic_workflow_tool(
    goal: str,
    ctx: Context,
    max_steps: int = 5,
    context_depth: str = "comprehensive",
) -> dict[str, Any]:
    """
    [SEP-1577] Autonomous 3-phase workflow: Plan → Execute → Audit via ctx.sample().

    Available tools: search_federated, rag_semantic_search, ingest_fleet_to_rag,
    glom_on, get_fleet_telemetry, rag_stats, rag_clear, universal_milestone,
    get_milestones_history.

    Args:
        goal: Natural language description of what to accomplish.
        max_steps: Maximum execution steps. Default: 5.
        context_depth: "basic" or "comprehensive". Default: "comprehensive".

    Returns:
        goal, correlation_id, plan, steps_taken, audit, timestamp.
    """
    cid = ctx.correlation_id
    await ctx.info(f"[{cid}] agentic_workflow_tool: goal={goal!r}")

    # Phase 1 — Build context
    context_block = ""
    if context_depth == "comprehensive":
        try:
            tel = await _get_fleet_telemetry_internal()
            ri = await _rag.stats()
            context_block = (
                f"\nFleet: {tel.get('fleet_status')} — {tel.get('active_nodes')} active nodes."
                f"\nRAG: {ri.get('total_items', 0)} items indexed ({ri.get('embedding_model', 'unknown')})."
            )
        except Exception:
            pass

    plan_prompt = f"""You are orchestrating the Universal Actuator MCP Hub.

Goal: {goal}{context_block}

Available tools:
- search_federated: {{query, domain="all"|"calibre"|"plex"|"immich"}}
- rag_semantic_search: {{query, limit=10, source=null}}
- ingest_fleet_to_rag: {{}}
- glom_on: {{}}
- get_fleet_telemetry: {{}}
- rag_stats: {{}}
- rag_clear: {{}}
- universal_milestone: {{title, description, kind="info"}}
- get_milestones_history: {{}}

Return ONLY valid JSON, no markdown fences:
{{"steps": [{{"step": 1, "tool": "tool_name", "args": {{}}, "rationale": "why"}}], "expected_outcome": "description"}}"""

    try:
        raw = await ctx.sample(plan_prompt)
        # Clean up JSON if LLM added fences
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        plan = json.loads(clean)
    except Exception as e:
        logger.warning(f"[{cid}] Plan parse failed ({e}), using fallback.")
        plan = {
            "steps": [{"step": 1, "tool": "get_fleet_telemetry", "args": {}, "rationale": "fallback health check"}],
            "expected_outcome": "Telemetry check",
        }

    await ctx.info(f"[{cid}] Plan: {len(plan.get('steps', []))} steps.")

    # Phase 2 — Execute
    steps_taken: list[dict[str, Any]] = []
    for step_def in plan.get("steps", [])[:max_steps]:
        tool_name = step_def.get("tool", "")
        args = step_def.get("args", {})
        await ctx.info(f"[{cid}] Step {step_def.get('step')}: {tool_name}")
        try:
            result = await _dispatch_tool(tool_name, args)
            steps_taken.append({"step": step_def, "result": str(result)[:800], "status": "success"})
        except Exception as e:
            steps_taken.append({"step": step_def, "error": str(e), "status": "failed"})
            await ctx.warning(f"[{cid}] Step failed: {e}")

    # Phase 3 — Audit
    success_count = sum(1 for s in steps_taken if s["status"] == "success")
    audit_prompt = f"""Audit this workflow execution:
Goal: {goal}
Steps ({success_count}/{len(steps_taken)} succeeded): {json.dumps([{{"tool": s["step"].get("tool"), "status": s["status"]}} for s in steps_taken])}

Return ONLY JSON: {{"achieved": true_or_false, "quality": "good|partial|failed", "issues": [], "next_steps": []}}"""

    try:
        raw = await ctx.sample(audit_prompt)
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        audit = json.loads(clean)
    except Exception:
        audit = {"achieved": success_count > 0, "quality": "partial" if success_count > 0 else "failed", "issues": [], "next_steps": []}

    await ctx.info(f"[{cid}] Done. Achieved={audit.get('achieved')} Quality={audit.get('quality')}")

    return {
        "goal": goal,
        "correlation_id": cid,
        "plan": plan,
        "steps_taken": steps_taken,
        "audit": audit,
        "steps_executed": len(steps_taken),
        "steps_succeeded": success_count,
        "timestamp": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@mcp.custom_route("/api/v1/health", methods=["GET"])
async def health(request):
    ri = await _rag.stats()
    return JSONResponse({"status": "ok", "version": "2.0.0", "rag": ri, "timestamp": datetime.now().isoformat()})


@mcp.custom_route("/api/v1/glom_on", methods=["GET"])
async def glom_on_rest(request):
    res = await _glom_on_internal()
    return JSONResponse(res)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Standard SSE port for Universal Actuator Hub (aligned to 10745 from reservoir)
    mcp.run(transport="sse", port=10745)
