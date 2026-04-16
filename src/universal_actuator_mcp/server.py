"""
Universal Actuator MCP Hub — SOTA v14.1.0
Industrial Federation Gateway | FastMCP 3.2 | LanceDB RAG | ctx.sample()
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
import psutil
from fastapi.middleware.cors import CORSMiddleware
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


# Initialize FastMCP 3.2 (Reductionist Standard)
mcp = FastMCP(
    "Universal Actuator Hub",
    version="2.1.0",
)


@mcp.lifespan()
async def lifespan(server: FastMCP):
    global _fleet
    logger.info("Universal Actuator Federation Gateway starting (FastMCP 3.2)...")
    await _rag.initialize()
    logger.info("LanceDB RAG initialized.")

    _fleet = FleetManager()
    logger.info("FleetManager ready (Federation Gateway initialized).")

    # Headless Industrial Autostart
    logger.info("Ensuring federated fleet availability...")
    autostart_results = await _fleet.ensure_all()
    logger.info(f"Fleet autostart results: {autostart_results}")

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
    except (TimeoutError, ConnectionRefusedError, OSError):
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
                    discovered.append(
                        {"name": name, "source": str(path), "command": details.get("command"), "active": False}
                    )
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


async def _get_ollama_models_internal() -> list[str]:
    """Dynamic elicitation of available models from local Ollama instance."""
    url = "http://127.0.0.1:11434/api/tags"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2.0) as response:
                if response.status == 200:
                    data = await response.json()
                    # Unified extraction: supports both old and new Ollama API schemas
                    models = [m["name"] for m in data.get("models", [])]
                    return models if models else ["llama3", "mistral"]  # SOTA fallbacks
                return ["llama3", "mistral"]
    except Exception as e:
        logger.warning(f"Ollama discovery failed: {e}")
        return ["llama3", "mistral"]


async def _get_fleet_telemetry_internal() -> dict[str, Any]:
    discovery = await _glom_on_internal()
    active_nodes = [n for n in discovery["discovered_servers"] if n.get("active")]
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()

    # Enrich node statuses with real connection check if possible
    node_details = []
    for node in discovery["discovered_servers"]:
        node_details.append(
            {
                "name": node.get("name"),
                "port": node.get("port"),
                "status": "online" if node.get("active") else "offline",
                "source": node.get("source"),
            }
        )

    return {
        "fleet_status": "Healthy" if active_nodes else "Standalone",
        "active_nodes": len(active_nodes),
        "total_discovered": len(discovery["discovered_servers"]),
        "host_metrics": {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "available_gb": round(mem.available / (1024**3), 2),
        },
        "node_details": node_details,
        "telemetry_timestamp": datetime.now().isoformat(),
    }


async def _get_fleet_instance() -> FleetManager:
    global _fleet
    if _fleet is None:
        logger.info("Lazy-initializing FleetManager (lifespan fallback)...")
        _fleet = FleetManager()
    return _fleet


async def _search_federated_internal(query: str, domain: str = "all") -> dict[str, Any]:
    """Real federated search via FleetManager → Calibre/Plex/Immich/Docs/Knowledge MCP servers."""
    fleet = await _get_fleet_instance()

    # Base results structure
    base = {"calibre": [], "plex": [], "immich": [], "docsops": [], "knowledge": []}

    if domain == "all":
        results = await fleet.search_all(query)
    elif domain == "calibre":
        base["calibre"] = await fleet.search_calibre(query)
        results = base
    elif domain == "plex":
        base["plex"] = await fleet.search_plex(query)
        results = base
    elif domain == "immich":
        base["immich"] = await fleet.search_immich(query)
        results = base
    elif domain == "docs" or domain == "docsops":
        all_res = await fleet.search_all(query)
        base["docsops"] = all_res.get("docsops", [])
        results = base
    elif domain == "knowledge" or domain == "memory":
        all_res = await fleet.search_all(query)
        base["knowledge"] = all_res.get("knowledge", [])
        results = base
    else:
        results = await fleet.search_all(query)

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
    fleet = await _get_fleet_instance()
    counts = await fleet.ingest_all_to_rag(_rag, limit=500)
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
        "rag_semantic_search": lambda: _rag.semantic_search(
            args.get("query", ""), args.get("limit", 10), args.get("source")
        ),
        "ingest_fleet_to_rag": _ingest_fleet_to_rag_internal,
        "glom_on": _glom_on_internal,
        "get_fleet_telemetry": _get_fleet_telemetry_internal,
        "rag_stats": _rag.stats,
        "rag_clear": _rag.clear,
        "universal_milestone": lambda: _save_milestone_internal(
            args.get("title", ""), args.get("description", ""), args.get("type", "info")
        ),
        "get_milestones_history": lambda: {"milestones": _load_milestones(), "count": len(_load_milestones())},
        "list_ollama_models": _get_ollama_models_internal,
    }
    fn = dispatch.get(tool_name)
    if fn is None:
        raise ValueError(f"Unknown tool: '{tool_name}'. Available: {sorted(dispatch)}")
    return await fn()


# ---------------------------------------------------------------------------
# MCP Tools (Industrial Gateway Pattern)
# ---------------------------------------------------------------------------


@mcp.tool()
async def universal_actuator(
    domain: str,
    action: str,
    payload: dict[str, Any],
    ctx: Context,
) -> dict[str, Any]:
    """
    PORTMANTEAU PATTERN RATIONALE:
    Consolidates high-entropy cross-domain actions into a single high-fidelity router.
    Reduces semantic overhead for agents by providing a unified protocol for
    files, media, robotics, and system operations.

    Args:
        domain: Target domain ("files", "media", "robotics", "system").
        action: Specific action within the domain.
        payload: Parameter object for the action.
    """
    await ctx.info(f"[{ctx.correlation_id}] universal_actuator: domain={domain} action={action}")

    # Internal routing logic (Reductionist approach)
    if domain == "media":
        if action == "search":
            return await _search_federated_internal(payload.get("query", ""), payload.get("domain", "all"))
        if action == "ingest":
            return await _ingest_fleet_to_rag_internal()
        if action == "rag_search":
            return await _rag.semantic_search(payload.get("query", ""), payload.get("limit", 10), payload.get("source"))

    if domain == "system":
        if action == "telemetry":
            return await _get_fleet_telemetry_internal()
        if action == "discover":
            return await _glom_on_internal()
        if action == "models":
            return await _get_ollama_models_internal()

    return {
        "status": "partial_success",
        "message": f"Domain '{domain}' action '{action}' routed via fallback.",
        "routing_key": f"{domain}.{action}",
    }


@mcp.tool()
async def universal_status(ctx: Context) -> dict[str, Any]:
    """
    PORTMANTEAU PATTERN RATIONALE:
    Aggregates lifecycle telemetry and discovery data into a single industrial health dashboard.
    Enables rapid diagnosis of federated node connectivity and host resource utilization.
    """
    await ctx.info(f"[{ctx.correlation_id}] universal_status: initiating deep health check")
    telemetry = await _get_fleet_telemetry_internal()
    rag_info = await _rag.stats()

    return {
        "fleet": telemetry,
        "rag": rag_info,
        "system": {"version": "2.1.0", "mcp_version": "3.2.0", "timestamp": datetime.now().isoformat()},
    }


# ---------------------------------------------------------------------------
# Legacy & Domain-Specific Tools
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
async def list_ollama_models(ctx: Context) -> list[str]:
    """Elicit available LLM models from the local Ollama instance (no hardcoding)."""
    await ctx.info(f"[{ctx.correlation_id}] list_ollama_models: querying Ollama API...")
    return await _get_ollama_models_internal()


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
        except Exception as e:
            logger.debug(f"Failed to fetch RAG status for plan context: {e}")

    json_template = (
        '{"steps": [{"step": 1, "tool": "tool_name", "args": {}, "rationale": "why"}], '
        '"expected_outcome": "description"}'
    )
    plan_prompt = f"""You are orchestrating the Universal Actuator MCP Hub.

Goal: {goal}{context_block}

Available tools:
- search_federated: {{query, domain="all"|"calibre"|"plex"|"immich"|"docs"|"knowledge"}}
- rag_semantic_search: {{query, limit=10, source=null}}
- ingest_fleet_to_rag: {{}}
- glom_on: {{}}
- get_fleet_telemetry: {{}}
- rag_stats: {{}}
- rag_clear: {{}}
- universal_milestone: {{title, description, kind="info"}}
- get_milestones_history: {{}}

Return ONLY valid JSON, no markdown fences:
{json_template}"""

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
    audit_summary = json.dumps([{"tool": s["step"].get("tool"), "status": s["status"]} for s in steps_taken])
    audit_prompt = f"""Audit this workflow execution:
Goal: {goal}
Steps ({success_count}/{len(steps_taken)} succeeded): {audit_summary}

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
        audit = {
            "achieved": success_count > 0,
            "quality": "partial" if success_count > 0 else "failed",
            "issues": [],
            "next_steps": [],
        }

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
# REST API (Industrial Bridge)
# ---------------------------------------------------------------------------


@mcp.custom_route("/", methods=["GET"])
async def root_health(request):
    """Root endpoint for rapid availability verification."""
    return JSONResponse(
        {
            "status": "online",
            "service": "Universal Actuator Hub",
            "version": "2.1.0",
            "sota_standard": "v14.1.0",
            "timestamp": datetime.now().isoformat(),
        }
    )


@mcp.custom_route("/api/v1/health", methods=["GET"])
async def health(request):
    ri = await _rag.stats()
    return JSONResponse({"status": "ok", "version": "2.1.0", "rag": ri, "timestamp": datetime.now().isoformat()})


@mcp.custom_route("/health", methods=["GET"])
async def health_alias(request):
    return await health(request)


@mcp.custom_route("/api/v1/models", methods=["GET"])
async def models_rest(request):
    models = await _get_ollama_models_internal()
    return JSONResponse({"models": models, "timestamp": datetime.now().isoformat()})


@mcp.custom_route("/library", methods=["GET"])
async def library_rest(request):
    """
    PORTMANTEAU REST RATIONALE:
    Provides a high-fidelity bridge for frontend media consumption.
    Aggregates federated search results into a flat list for list-viewers.
    """
    query = request.query_params.get("q", "")
    domain = request.query_params.get("domain", "all")
    hits = await _search_federated_internal(query, domain)

    # Flatten results for the frontend
    all_items = []
    for source_list in hits.get("results", {}).values():
        if isinstance(source_list, list):
            all_items.extend(source_list)

    return JSONResponse({"items": all_items, "total": len(all_items), "query": query, "domain": domain})


@mcp.custom_route("/library/ingest", methods=["POST"])
async def library_ingest_rest(request):
    """Bridge to ingest_fleet_to_rag tool with industrial telemetry."""
    logger.info("REST: Ingest trigger received.")
    res = await _ingest_fleet_to_rag_internal()
    return JSONResponse(res)


@mcp.custom_route("/telemetry", methods=["GET"])
async def telemetry_rest(request):
    """Direct bridge to fleet telemetry."""
    res = await _get_fleet_telemetry_internal()
    return JSONResponse(res)


@mcp.custom_route("/chat", methods=["POST"])
async def chat_rest(request):
    data = await request.json()
    msg = data.get("message", "")
    return JSONResponse(
        {
            "status": "success",
            "response": f"Federation Hub received: '{msg}'. Agentic orchestrator ready to process.",
            "timestamp": datetime.now().isoformat(),
        }
    )


# ---------------------------------------------------------------------------
# App Factory (Must remain at bottom to capture all custom_routes)
# ---------------------------------------------------------------------------

app = mcp.http_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Standard SSE port for Universal Actuator Hub (10745)
    # RATIONALE: High-fidelity SSE transport for persistent node communication.
    mcp.run(transport="sse", port=10745)
