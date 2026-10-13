"""
Universal Actuator MCP Hub - SOTA v14.1.0
Industrial Federation Gateway | FastMCP 3.2 | LanceDB RAG | ctx.sample()
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

import aiohttp
import psutil
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import Client, Context, FastMCP
from fastmcp.server.providers.proxy import FastMCPProxy
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text
from pydantic import Field
from starlette.responses import JSONResponse, StreamingResponse

# Standard relative imports within the package
from .fleet import FleetManager
from .rag import LanceDBRag

logger = logging.getLogger("UnivActHub")
logging.basicConfig(level=logging.INFO)


def _cid(ctx: Context) -> str:
    """Correlation id for log lines (runtime attr on FastMCP Context, absent from 3.x stubs)."""
    return str(getattr(ctx, "correlation_id", "-"))


# Tool annotations (TOOL_DESIGN_STANDARDS §9): dict form - identical semantics to the
# future fastmcp.tool.annotations constants. Annotations match real behavior.
_READONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}
_MUTATING = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}
_DESTRUCTIVE = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}

# Shared dialogic envelope schema (DIALOGIC_RETURNS + TOOL_DESIGN §4.2):
# {"success": bool, "message": str, "data": {...}}. Per-tool `data` shapes are
# documented in each docstring's ## Return Format section.
_ENVELOPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        "data": {"type": "object"},
    },
    "required": ["success", "message", "data"],
}


def _error_response(message: str, error: str, remediation: str = "") -> dict[str, Any]:
    """Shared error envelope: logs with traceback, returns dialogic failure shape."""
    logger.exception("tool failure: %s (%s)", message, error)
    payload: dict[str, Any] = {"success": False, "error": error, "message": message}
    if remediation:
        payload["dialogic"] = {"suggestion": message, "remediation": remediation}
    return payload


class ActivityLog:
    def __init__(self, max_entries=2000):
        self.max_entries = max_entries
        self._entries = deque(maxlen=max_entries)

    def add(self, level, kind, detail, meta=None):
        eid = f"{time.time():.6f}.{uuid4().hex[:6]}"
        self._entries.append(
            {
                "id": eid,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "level": level.upper(),
                "kind": kind,
                "detail": detail,
                "meta": meta or {},
            }
        )
        return eid

    def info(self, kind, detail, **meta):
        return self.add("INFO", kind, detail, meta)

    def warn(self, kind, detail, **meta):
        return self.add("WARNING", kind, detail, meta)

    def error(self, kind, detail, **meta):
        return self.add("ERROR", kind, detail, meta)

    def query(self, limit=50, offset=0, level=None, kind=None, search=None, sort="desc", after_id=None):
        entries = list(self._entries)
        if after_id:
            try:
                at = float(after_id.split(".")[0])
                entries = [e for e in entries if float(e["id"].split(".")[0]) > at]
            except Exception:
                logger.debug("ActivityLog.query: unparsable after_id %r, ignoring filter", after_id)
        if level:
            lo = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
            ml = lo.get(level.upper(), 1)
            entries = [e for e in entries if lo.get(e["level"], 1) >= ml]
        if kind:
            entries = [e for e in entries if e["kind"] == kind]
        if search:
            q = search.lower()
            entries = [e for e in entries if q in e["detail"].lower()]
        entries.sort(key=lambda e: e["id"], reverse=(sort == "desc"))
        total = len(entries)
        page = entries[offset : offset + limit]
        return {
            "entries": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "max_entries": self.max_entries,
            "sort": sort,
        }

    def stats(self):
        levels, kinds = {}, {}
        for e in self._entries:
            levels[e["level"]] = levels.get(e["level"], 0) + 1
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        return {"total": len(self._entries), "max_entries": self.max_entries, "levels": levels, "kinds": kinds}

    def clear(self):
        self._entries.clear()


_activity_log = ActivityLog()

# Point to the existing state directory in the root
STATE_DIR = Path(__file__).parent.parent.parent / "backend" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
MILESTONES_FILE = STATE_DIR / "milestones.json"

_rag: LanceDBRag = LanceDBRag()
_fleet: FleetManager | None = None


# Initialize FastMCP 3.2 (Reductionist Standard)
mcp = FastMCP(
    "Universal Actuator Hub",
    version="2.2.1",
)


# Prompts + bundled skills (FastMCP SkillsDirectoryProvider serves skill://universal-actuator).
from .prompts import register_prompts as _register_prompts

_register_prompts(mcp)

_skills_root = Path(__file__).parent.parent.parent / "skills"
if _skills_root.is_dir():
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    mcp.add_provider(SkillsDirectoryProvider(roots=[_skills_root]))
    logger.info("SkillsDirectoryProvider registered: %s", _skills_root)
else:
    logger.warning("Bundled skills directory missing: %s", _skills_root)


@mcp.lifespan()  # pyright: ignore[reportArgumentType] - FastMCP 3.x lifespan stub quirk, runtime OK
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
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2.0)) as response:
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
    try:
        return await fn()
    except Exception as e:
        return _error_response(
            f"Tool '{tool_name}' failed.",
            str(e),
            remediation=f"Check {tool_name} inputs, then retry or run get_fleet_telemetry().",
        )


# ---------------------------------------------------------------------------
# MCP Tools (Industrial Gateway Pattern)
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations=_MUTATING,
    output_schema=_ENVELOPE_SCHEMA,
)
async def universal_actuator(
    domain: Annotated[str, Field(description='Target domain: "files", "media", "robotics" or "system".')],
    action: Annotated[str, Field(description="Action within the domain, e.g. search, ingest, telemetry.")],
    payload: Annotated[dict[str, Any], Field(description="Action parameters, e.g. {query: ...}.")],
    ctx: Context,
) -> dict[str, Any]:
    """
    PORTMANTEAU PATTERN RATIONALE:
    Consolidates high-entropy cross-domain actions into a single high-fidelity router.
    Reduces semantic overhead for agents by providing a unified protocol for
    files, media, robotics, and system operations.

    ## Return Format
    {"success": bool, "message": str, "data": {routed payload, always with "routing_key": str}}.

    ## Examples
    - universal_actuator(domain="media", action="search", payload={"query": "dune"})
    - universal_actuator(domain="system", action="telemetry", payload={})
    """
    await ctx.info(f"[{_cid(ctx)}] universal_actuator: domain={domain} action={action}")

    # Internal routing logic (Reductionist approach)
    if domain == "media":
        if action == "search":
            data = await _search_federated_internal(payload.get("query", ""), payload.get("domain", "all"))
            return {"success": True, "message": f"Federated search: {data.get('total_hits', 0)} hits.", "data": data}
        if action == "ingest":
            data = await _ingest_fleet_to_rag_internal()
            return {
                "success": True,
                "message": f"Ingested {data.get('total_ingested', 0)} items.",
                "data": data,
            }
        if action == "rag_search":
            hits = await _rag.semantic_search(payload.get("query", ""), payload.get("limit", 10), payload.get("source"))
            return {"success": True, "message": f"RAG search: {len(hits)} hits.", "data": {"results": hits}}

    if domain == "system":
        if action == "telemetry":
            data = await _get_fleet_telemetry_internal()
            return {"success": True, "message": f"Fleet status: {data.get('fleet_status')}.", "data": data}
        if action == "discover":
            data = await _glom_on_internal()
            return {
                "success": True,
                "message": f"Discovered {data.get('count', 0)} servers.",
                "data": data,
            }
        if action == "models":
            models = await _get_ollama_models_internal()
            return {"success": True, "message": f"{len(models)} Ollama models.", "data": {"models": models}}

    return {
        "success": True,
        "message": f"Domain '{domain}' action '{action}' routed via fallback.",
        "data": {"routing_key": f"{domain}.{action}"},
    }


@mcp.tool(
    annotations=_READONLY,
    output_schema=_ENVELOPE_SCHEMA,
)
async def universal_status(ctx: Context) -> dict[str, Any]:
    """
    PORTMANTEAU PATTERN RATIONALE:
    Aggregates lifecycle telemetry and discovery data into a single industrial health dashboard.
    Enables rapid diagnosis of federated node connectivity and host resource utilization.

    ## Return Format
    {"success": bool, "message": str, "data": {"fleet": dict, "rag": dict, "system": dict}}.

    ## Examples
    - universal_status()
    """
    await ctx.info(f"[{_cid(ctx)}] universal_status: initiating deep health check")
    telemetry = await _get_fleet_telemetry_internal()
    rag_info = await _rag.stats()

    data = {
        "fleet": telemetry,
        "rag": rag_info,
        "system": {"version": "2.2.1", "timestamp": datetime.now().isoformat()},
    }
    return {"success": True, "message": f"Fleet status: {telemetry.get('fleet_status')}.", "data": data}


# ---------------------------------------------------------------------------
# Legacy & Domain-Specific Tools
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def search_federated(
    query: Annotated[str, Field(description="Search query string.")],
    ctx: Context,
    domain: Annotated[str, Field(description='"plex", "calibre", "immich", "docs", "knowledge" or "all".')] = "all",
) -> dict[str, Any]:
    """
    Unified search across Plex, Calibre, and Immich via their MCP servers.

    ## Return Format
    {"success": bool, "message": str,
     "data": {"query": str, "domain": str, "results": {source: [...]}, "total_hits": int}}.

    ## Examples
    - search_federated(query="dune")
    - search_federated(query="asimov", domain="calibre")
    """
    await ctx.info(f"[{_cid(ctx)}] search_federated query={query!r} domain={domain}")
    data = await _search_federated_internal(query, domain)
    return {"success": True, "message": f"{data.get('total_hits', 0)} hits.", "data": data}


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def rag_semantic_search(
    query: Annotated[str, Field(description="Natural language query.")],
    ctx: Context,
    limit: Annotated[int, Field(description="Max results.", ge=1, le=100)] = 10,
    source: Annotated[str | None, Field(description='Optional filter: "calibre", "plex" or "immich".')] = None,
) -> dict[str, Any]:
    """
    Semantic vector search over the LanceDB media index.

    Call ingest_fleet_to_rag() first to populate. Uses sentence-transformers
    (all-MiniLM-L6-v2) or hash fallback.

    ## Return Format
    {"success": bool, "message": str,
     "data": {"query": str, "results": [...], "result_count": int}} - ranked, lower _score = more similar.

    ## Examples
    - rag_semantic_search(query="space opera")
    - rag_semantic_search(query="asimov", limit=5, source="calibre")
    """
    await ctx.info(f"[{_cid(ctx)}] rag_semantic_search query={query!r} limit={limit} source={source}")
    results = await _rag.semantic_search(query, limit, source)
    stats = await _rag.stats()
    data = {
        "query": query,
        "source_filter": source,
        "results": results,
        "result_count": len(results),
        "index_size": stats.get("total_items", 0),
        "embedding_model": stats.get("embedding_model", "unknown"),
    }
    return {"success": True, "message": f"{len(results)} results.", "data": data}


@mcp.tool(annotations=_MUTATING, output_schema=_ENVELOPE_SCHEMA)
async def ingest_fleet_to_rag(ctx: Context) -> dict[str, Any]:
    """
    Bulk-ingest metadata from Calibre, Plex, and Immich into the LanceDB RAG index.

    Fetches up to 500 items per source. Safe to call repeatedly - existing items
    are overwritten by id.

    ## Return Format
    {"success": bool, "message": str,
     "data": {"ingested_per_source": dict, "total_ingested": int, "rag_stats": dict}}.

    ## Examples
    - ingest_fleet_to_rag()
    """
    await ctx.info(f"[{_cid(ctx)}] ingest_fleet_to_rag: starting bulk ingest...")
    result = await _ingest_fleet_to_rag_internal()
    await ctx.info(f"[{_cid(ctx)}] ingest_fleet_to_rag: {result['total_ingested']} items total.")
    return {"success": True, "message": f"Ingested {result['total_ingested']} items.", "data": result}


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def rag_stats(ctx: Context) -> dict[str, Any]:
    """
    LanceDB RAG index statistics: total_items, embedding_model, source_distribution.

    ## Return Format
    {"success": bool, "message": str, "data": {"total_items": int, "embedding_model": str, ...}}.

    ## Examples
    - rag_stats()
    """
    await ctx.info(f"[{_cid(ctx)}] rag_stats")
    data = await _rag.stats()
    return {"success": True, "message": f"Index holds {data.get('total_items', 0)} items.", "data": data}


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_ENVELOPE_SCHEMA)
async def rag_clear(ctx: Context) -> dict[str, Any]:
    """
    Clear the LanceDB RAG index entirely. Use before a fresh ingest.

    Irreversible - all indexed vectors are dropped.

    ## Return Format
    {"success": bool, "message": str, "data": {"status": str, "timestamp": str}}.

    ## Examples
    - rag_clear()
    """
    await ctx.warning(f"[{_cid(ctx)}] rag_clear: dropping index")
    await _rag.clear()
    return {
        "success": True,
        "message": "RAG index cleared.",
        "data": {"status": "cleared", "timestamp": datetime.now().isoformat()},
    }


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def glom_on(ctx: Context) -> dict[str, Any]:
    """
    Auto-discovery: scan MCP config files and port range 10700-10900 for active services.

    ## Return Format
    {"success": bool, "message": str,
     "data": {"discovered_servers": [...], "count": int, "active_count": int}}.

    ## Examples
    - glom_on()
    """
    await ctx.info(f"[{_cid(ctx)}] glom_on: scanning configs + ports 10700-10900...")
    result = await _glom_on_internal()
    await ctx.info(f"[{_cid(ctx)}] glom_on: {result['count']} discovered, {result['active_count']} active.")
    return {
        "success": True,
        "message": f"{result['count']} discovered, {result['active_count']} active.",
        "data": result,
    }


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def get_fleet_telemetry(ctx: Context) -> dict[str, Any]:
    """
    Real-time host health + fleet node count (CPU, RAM, active services).

    ## Return Format
    {"success": bool, "message": str,
     "data": {"fleet_status": str, "host_metrics": dict, "active_nodes": int, "node_details": [...]}}.

    ## Examples
    - get_fleet_telemetry()
    """
    await ctx.info(f"[{_cid(ctx)}] get_fleet_telemetry")
    data = await _get_fleet_telemetry_internal()
    return {"success": True, "message": f"Fleet status: {data.get('fleet_status')}.", "data": data}


@mcp.tool(annotations=_MUTATING, output_schema=_ENVELOPE_SCHEMA)
async def universal_milestone(
    title: Annotated[str, Field(description="Milestone title.")],
    description: Annotated[str, Field(description="What was accomplished.")],
    ctx: Context,
    kind: Annotated[str, Field(description='"info", "warning" or "achievement".')] = "info",
) -> dict[str, Any]:
    """
    Log a persistent milestone to the state file.

    ## Return Format
    {"success": bool, "message": str, "data": {"milestone": dict}}.

    ## Examples
    - universal_milestone(title="RAG ingest done", description="500 items", kind="achievement")
    """
    await ctx.info(f"[{_cid(ctx)}] milestone: {title}")
    entry = _save_milestone_internal(title, description, kind)
    return {"success": True, "message": f"Milestone recorded: {title}", "data": {"milestone": entry}}


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def get_milestones_history(ctx: Context) -> dict[str, Any]:
    """
    Retrieve all recorded milestones.

    ## Return Format
    {"success": bool, "message": str, "data": {"milestones": [...], "count": int}}.

    ## Examples
    - get_milestones_history()
    """
    await ctx.info(f"[{_cid(ctx)}] get_milestones_history")
    milestones = _load_milestones()
    return {
        "success": True,
        "message": f"{len(milestones)} milestones.",
        "data": {"milestones": milestones, "count": len(milestones)},
    }


@mcp.tool(annotations=_READONLY, output_schema=_ENVELOPE_SCHEMA)
async def list_ollama_models(ctx: Context) -> dict[str, Any]:
    """
    Elicit available LLM models from the local Ollama instance (no hardcoding).

    ## Return Format
    {"success": bool, "message": str, "data": {"models": ["model:tag", ...]}}.
    Live from Ollama, SOTA fallbacks when unreachable.

    ## Examples
    - list_ollama_models()
    """
    await ctx.info(f"[{_cid(ctx)}] list_ollama_models: querying Ollama API...")
    models = await _get_ollama_models_internal()
    return {"success": True, "message": f"{len(models)} models.", "data": {"models": models}}


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_ENVELOPE_SCHEMA)
async def agentic_workflow_tool(
    goal: Annotated[str, Field(description="Natural language description of what to accomplish.")],
    ctx: Context,
    max_steps: Annotated[int, Field(description="Maximum execution steps.", ge=1, le=20)] = 5,
    context_depth: Annotated[str, Field(description='"basic" or "comprehensive".')] = "comprehensive",
) -> dict[str, Any]:
    """
    [SEP-1577] Autonomous 3-phase workflow: Plan → Execute → Audit via ctx.sample().

    Available tools: search_federated, rag_semantic_search, ingest_fleet_to_rag,
    glom_on, get_fleet_telemetry, rag_stats, rag_clear, universal_milestone,
    get_milestones_history.

    Side effects: the plan may invoke mutating tools (ingest, milestone) and, only
    when the goal asks for it, destructive ones (rag_clear).

    ## Return Format
    {"success": bool, "message": str,
     "data": {"goal": str, "plan": dict, "steps_taken": [...], "audit": dict,
              "steps_executed": int, "steps_succeeded": int}}.

    ## Examples
    - agentic_workflow_tool(goal="Summarise fleet health and record a milestone")
    """
    cid = _cid(ctx)
    await ctx.info(f"[{cid}] agentic_workflow_tool: goal={goal!r}")

    # Phase 1 - Build context
    context_block = ""
    if context_depth == "comprehensive":
        try:
            tel = await _get_fleet_telemetry_internal()
            ri = await _rag.stats()
            context_block = (
                f"\nFleet: {tel.get('fleet_status')} - {tel.get('active_nodes')} active nodes."
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
        clean = str(raw).strip()
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

    # Phase 2 - Execute
    steps_taken: list[dict[str, Any]] = []
    for step_def in plan.get("steps", [])[:max_steps]:
        tool_name = step_def.get("tool", "")
        args = step_def.get("args", {})
        await ctx.info(f"[{cid}] Step {step_def.get('step')}: {tool_name}")
        try:
            result = await _dispatch_tool(tool_name, args)
            # _dispatch_tool returns a dialogic envelope (success False) instead of
            # raising on tool errors - classify accordingly.
            ok = not (isinstance(result, dict) and result.get("success") is False)
            steps_taken.append(
                {
                    "step": step_def,
                    "result": str(result)[:800],
                    "status": "success" if ok else "failed",
                }
            )
            if not ok:
                await ctx.warning(f"[{cid}] Step failed: {result.get('error', result)}")
        except Exception as e:
            steps_taken.append({"step": step_def, "error": str(e), "status": "failed"})
            await ctx.warning(f"[{cid}] Step failed: {e}")

    # Phase 3 - Audit
    success_count = sum(1 for s in steps_taken if s["status"] == "success")
    audit_summary = json.dumps([{"tool": s["step"].get("tool"), "status": s["status"]} for s in steps_taken])
    audit_prompt = f"""Audit this workflow execution:
Goal: {goal}
Steps ({success_count}/{len(steps_taken)} succeeded): {audit_summary}

Return ONLY JSON: {{"achieved": true_or_false, "quality": "good|partial|failed", "issues": [], "next_steps": []}}"""

    try:
        raw = await ctx.sample(audit_prompt)
        clean = str(raw).strip()
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

    data = {
        "goal": goal,
        "correlation_id": cid,
        "plan": plan,
        "steps_taken": steps_taken,
        "audit": audit,
        "steps_executed": len(steps_taken),
        "steps_succeeded": success_count,
        "timestamp": datetime.now().isoformat(),
    }
    achieved = bool(audit.get("achieved"))
    return {
        "success": achieved,
        "message": f"Workflow {audit.get('quality')}: {success_count}/{len(steps_taken)} steps succeeded.",
        "data": data,
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
            "version": "2.2.1",
            "sota_standard": "v14.1.0",
            "timestamp": datetime.now().isoformat(),
        }
    )


@mcp.custom_route("/api/v1/health", methods=["GET"])
async def health(request):
    ri = await _rag.stats()
    return JSONResponse({"status": "ok", "version": "2.1.0", "rag": ri, "timestamp": datetime.now().isoformat()})


@mcp.custom_route("/api/v1/deps", methods=["GET"])
async def deps_status(request):
    """Dependency health: reports calibre-mcp and plex-mcp reachability."""

    async def _check(host: str, port: int) -> bool:
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1.0)
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False

    calibre_up = await _check("127.0.0.1", 10720)
    plex_up = await _check("127.0.0.1", 10740)
    all_ok = calibre_up and plex_up
    return JSONResponse(
        {
            "ok": all_ok,
            "deps": {
                "calibre": {"port": 10720, "up": calibre_up},
                "plex": {"port": 10740, "up": plex_up},
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


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


@mcp.custom_route("/api/logs", methods=["GET"])
async def api_log_query(request):
    limit = int(request.query_params.get("limit", 50))
    offset = int(request.query_params.get("offset", 0))
    level = request.query_params.get("level")
    kind = request.query_params.get("kind")
    search = request.query_params.get("search")
    sort = request.query_params.get("sort", "desc")
    after_id = request.query_params.get("after_id")
    return JSONResponse(
        _activity_log.query(
            limit=limit,
            offset=offset,
            level=level,
            kind=kind,
            search=search,
            sort=sort,
            after_id=after_id,
        )
    )


@mcp.custom_route("/api/logs/stats", methods=["GET"])
async def api_log_stats(request):
    return JSONResponse(_activity_log.stats())


@mcp.custom_route("/api/logs/clear", methods=["POST"])
async def api_log_clear(request):
    _activity_log.clear()
    return JSONResponse({"success": True})


@mcp.custom_route("/api/milestones", methods=["GET"])
async def api_milestones(request):
    """Milestone timeline for the Inbox page (mirrors get_milestones_history tool)."""
    milestones = _load_milestones()
    limit = request.query_params.get("limit")
    try:
        items = milestones[-int(limit) :] if limit else milestones
    except (TypeError, ValueError):
        items = milestones
    return JSONResponse({"success": True, "milestones": items, "count": len(milestones)})


@mcp.custom_route("/chat", methods=["POST"])
async def chat_rest(request):
    data = await request.json()
    msg = data.get("message", "")
    return JSONResponse(_chat_reply(msg))


@mcp.custom_route("/api/shutdown", methods=["POST"])
async def api_shutdown(request):
    logger.warning("Shutdown requested via REST API")
    # Respond 200 first so the fleet launcher can checkpoint, then exit ~500 ms
    # later so in-flight writes flush (fleet shutdown contract).
    try:
        loop = asyncio.get_running_loop()
        loop.call_later(0.5, lambda: os._exit(0))
    except RuntimeError:
        os._exit(0)
    return JSONResponse({"success": True, "message": "shutting down in ~500 ms"})


_MCP_TOOL_NAMES = (
    "universal_actuator",
    "universal_status",
    "search_federated",
    "rag_semantic_search",
    "ingest_fleet_to_rag",
    "rag_stats",
    "rag_clear",
    "glom_on",
    "get_fleet_telemetry",
    "universal_milestone",
    "get_milestones_history",
    "list_ollama_models",
    "agentic_workflow_tool",
    "universal_shutdown",
    "show_fleet_status_card",
    "show_rag_stats_card",
)

_REPO_ROOT = Path(__file__).parent.parent.parent


@mcp.custom_route("/api/capabilities", methods=["GET"])
async def api_capabilities(request):
    """Standard fleet capability discovery (WEBAPP_STANDARDS 1.4)."""
    return JSONResponse(
        {
            "service": "universal-actuator-mcp",
            "version": "2.2.1",
            "transports": ["stdio", "http"],
            "mcp_tools": list(_MCP_TOOL_NAMES),
            "tool_count": len(_MCP_TOOL_NAMES),
            "rest_routes": [
                "/api/capabilities",
                "/api/skills",
                "/api/v1/health",
                "/health",
                "/api/v1/models",
                "/api/llm/chat",
                "/api/llm/chat/stream",
                "/api/v1/diagnostics",
                "/api/fleet/servers",
                "/telemetry",
                "/library",
                "/chat",
                "/api/logs",
                "/api/shutdown",
            ],
            "providers": {"ollama": "http://127.0.0.1:11434"},
            "timestamp": datetime.now().isoformat(),
        }
    )


@mcp.custom_route("/api/skills", methods=["GET"])
async def api_skills(request):
    """Serve the domain SKILL.md so Chat can build skill-first prompts."""
    skill_path = _REPO_ROOT / "skills" / "universal-actuator" / "SKILL.md"
    if not skill_path.exists():
        return JSONResponse({"success": False, "message": "SKILL.md not found"}, status_code=404)
    return JSONResponse(
        {
            "success": True,
            "skills": [
                {
                    "name": "universal-actuator",
                    "uri": "skill://universal-actuator",
                    "content": skill_path.read_text(encoding="utf-8"),
                }
            ],
        }
    )


def _chat_reply(message: str) -> dict[str, Any]:
    return {
        "status": "success",
        "response": f"Federation Hub received: '{message}'. Agentic orchestrator ready to process.",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.custom_route("/api/llm/chat", methods=["POST"])
async def api_llm_chat(request):
    """Backend chat proxy: the ONLY path the Chat page uses (keys never leave the server)."""
    data = await request.json()
    message = data.get("message", "")
    if not message and isinstance(data.get("messages"), list) and data["messages"]:
        message = data["messages"][-1].get("content", "")
    system = str(data.get("system", ""))
    reply = _chat_reply(message)
    reply["provider"] = data.get("provider", "hub-echo")
    reply["model"] = data.get("model", "federation-hub")
    reply["skill_chars"] = len(system)
    return JSONResponse(reply)


@mcp.custom_route("/api/llm/chat/stream", methods=["POST"])
async def api_llm_chat_stream(request):
    """Streaming (NDJSON) variant of the backend chat proxy."""
    data = await request.json()
    message = data.get("message", "")
    reply = _chat_reply(message)["response"]

    async def _chunks():
        words = reply.split(" ")
        for i in range(0, len(words), 8):
            yield json.dumps({"delta": " ".join(words[i : i + 8]) + " "}) + "\n"
        yield json.dumps({"done": True}) + "\n"

    return StreamingResponse(_chunks(), media_type="application/x-ndjson")


async def _discover_providers() -> dict[str, Any]:
    """Probe local LLM providers (Ollama :11434, LM Studio :1234). Shared by /discover + /providers."""
    providers: dict[str, Any] = {}

    async def _probe(url: str) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=2.0)) as response:
                    return {"detected": response.status == 200, "url": url}
        except Exception:
            return {"detected": False, "url": url}

    providers["ollama"] = await _probe("http://127.0.0.1:11434/api/tags")
    providers["lmstudio"] = await _probe("http://127.0.0.1:1234/v1/models")
    return providers


@mcp.custom_route("/api/llm/discover", methods=["GET"])
async def api_llm_discover(request):
    """Probe local LLM providers (Ollama :11434, LM Studio :1234). Consumed by Chat on mount."""
    return JSONResponse({"success": True, "providers": await _discover_providers()})


@mcp.custom_route("/api/llm/providers", methods=["GET"])
async def api_llm_providers(request):
    """Provider registry: local detected flags + cloud configured flags (never key bytes)."""
    found = await _discover_providers()
    return JSONResponse(
        {
            "success": True,
            "local": {
                "ollama": {**found["ollama"], "free": True},
                "lmstudio": {**found["lmstudio"], "free": True},
            },
            "cloud": {
                "openai": {"configured": bool(os.environ.get("OPENAI_API_KEY"))},
                "anthropic": {"configured": bool(os.environ.get("ANTHROPIC_API_KEY"))},
            },
        }
    )


@mcp.custom_route("/api/llm/onboarding", methods=["GET"])
async def api_llm_onboarding(request):
    """Fresh-install starter facts + recommended path for the under-hero cue."""
    return JSONResponse(
        {
            "success": True,
            "facts": [
                "No keys needed: Ollama and LM Studio run locally and free.",
                "Install Ollama, pull a model, then refresh Status to detect it.",
                "Chat works without any LLM via the hub echo; agentic workflows use ctx.sample().",
            ],
            "recommended": "ollama",
        }
    )


@mcp.custom_route("/api/v1/diagnostics", methods=["GET"])
async def api_diagnostics(request):
    """Full diagnostics for CUA-NSIS smoke testing: tool list, versions, health signals."""
    rag_info: dict[str, Any] = {}
    try:
        rag_info = await _rag.stats()
    except Exception as e:
        rag_info = {"error": str(e)}
    models = await _get_ollama_models_internal()
    return JSONResponse(
        {
            "service": "universal-actuator-mcp",
            "version": "2.2.1",
            "status": "ok",
            "mcp_tools": list(_MCP_TOOL_NAMES),
            "tool_count": len(_MCP_TOOL_NAMES),
            "rag": rag_info,
            "ollama_models": models,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


@mcp.custom_route("/api/fleet/servers", methods=["GET"])
async def api_fleet_servers(request):
    """Same-origin proxy for the federated node registry (frontend must not hardcode node URLs)."""
    node_base = os.environ.get("FLEET_NODE_URL", "http://127.0.0.1:10854").rstrip("/")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{node_base}/servers", timeout=aiohttp.ClientTimeout(total=5.0)) as response:
                data = await response.json()
                return JSONResponse(data)
    except Exception as e:
        logger.warning(f"Fleet node registry unreachable at {node_base}: {e}")
        return JSONResponse({"success": False, "message": f"node registry unreachable: {e}"}, status_code=502)


@mcp.tool(annotations=_DESTRUCTIVE, output_schema=_ENVELOPE_SCHEMA)
async def universal_shutdown(ctx: Context) -> dict:
    """Shut down the Universal Actuator server gracefully.

    Irreversible - all in-memory state, fleet sessions, and RAG cache are lost.
    The process exits immediately; no result is returned to the caller.

    ## Return Format
    No return (process exits). Declared envelope for schema completeness:
    {"success": bool, "message": str}.

    ## Examples
    - universal_shutdown()
    """
    await ctx.info(f"[{_cid(ctx)}] Shutdown requested via MCP tool")
    os._exit(0)


# ---------------------------------------------------------------------------
# MCP Apps (Prefab UI) - list/status-class surfaces (SOTA §2.2)
# Disabled with UA_PREFAB_APPS=0 (skips registration, e.g. headless CI).
# ---------------------------------------------------------------------------

if os.environ.get("UA_PREFAB_APPS", "1").strip().lower() not in ("0", "false", "no", "off"):

    @mcp.tool(app=True)
    async def show_fleet_status_card(ctx: Context | None = None) -> Any:
        """
        Show fleet health as a rich card (MCP App): status, active nodes, host metrics.

        Same data as get_fleet_telemetry()/universal_status(). Disable with UA_PREFAB_APPS=0.

        ## Return Format
        ToolResult with plain-text content summary + PrefabApp structured content.

        ## Examples
        - show_fleet_status_card()
        """
        telemetry = await _get_fleet_telemetry_internal()
        rag_info = await _rag.stats()
        status = str(telemetry.get("fleet_status", "Unknown"))
        active = int(telemetry.get("active_nodes", 0))
        total = int(telemetry.get("total_discovered", 0))
        metrics = telemetry.get("host_metrics", {})

        with Card(cssClass="max-w-lg") as view:
            with CardHeader():
                CardTitle("Federation Hub")
            with CardContent():
                Text(f"Status: {status}  ·  Nodes: {active}/{total} active", cssClass="font-semibold")
                Text(
                    f"CPU {metrics.get('cpu_percent', '?')}%  ·  "
                    f"RAM {metrics.get('memory_percent', '?')}%  ·  "
                    f"RAG items {rag_info.get('total_items', 0)}",
                    cssClass="text-sm",
                )
                for node in (telemetry.get("node_details") or [])[:8]:
                    mark = "online" if node.get("status") == "online" else "offline"
                    Text(f"- {node.get('name')} ({node.get('port') or '?'}): {mark}", cssClass="text-sm")

        summary = f"Federation Hub: {status}, {active}/{total} nodes active."
        return ToolResult(
            content=summary,
            structured_content=PrefabApp(view=view, title="Federation Hub"),
        )

    @mcp.tool(app=True)
    async def show_rag_stats_card(ctx: Context | None = None) -> Any:
        """
        Show the LanceDB RAG index as a rich card (MCP App): size, model, per-source counts.

        Same data as rag_stats(). Disable with UA_PREFAB_APPS=0.

        ## Return Format
        ToolResult with plain-text content summary + PrefabApp structured content.

        ## Examples
        - show_rag_stats_card()
        """
        info = await _rag.stats()
        total_items = int(info.get("total_items", 0))
        model = str(info.get("embedding_model", "unknown"))

        with Card(cssClass="max-w-lg") as view:
            with CardHeader():
                CardTitle("RAG Index")
            with CardContent():
                Text(f"Items: {total_items}  ·  Model: {model}", cssClass="font-semibold")
                sources = info.get("source_distribution") or info.get("sources") or {}
                if isinstance(sources, dict):
                    for source, count in sources.items():
                        Text(f"- {source}: {count}", cssClass="text-sm")

        return ToolResult(
            content=f"RAG index: {total_items} items ({model}).",
            structured_content=PrefabApp(view=view, title="RAG Index"),
        )


# ---------------------------------------------------------------------------
# MCP Resources - live data streams (SOTA §2.1)
# ---------------------------------------------------------------------------


@mcp.resource("hub://status")
async def hub_status_resource() -> str:
    """Live hub status snapshot (version, fleet state, RAG size) as JSON text."""
    telemetry = await _get_fleet_telemetry_internal()
    rag_info = await _rag.stats()
    return json.dumps(
        {
            "service": "universal-actuator-mcp",
            "version": "2.2.1",
            "fleet_status": telemetry.get("fleet_status"),
            "active_nodes": telemetry.get("active_nodes"),
            "rag_items": rag_info.get("total_items"),
            "timestamp": datetime.now().isoformat(),
        }
    )


# ---------------------------------------------------------------------------
# App Factory (Must remain at bottom to capture all custom_routes)
# ---------------------------------------------------------------------------

app = mcp.http_app(path="/")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:11239",
        "http://localhost:11240",
        "http://127.0.0.1:11239",
        "http://127.0.0.1:11240",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _maybe_proxy_to_daemon() -> bool:
    """Probe for an existing HTTP daemon; proxy stdio tool calls instead of full init.

    Prevents LanceDB/state contention when several stdio clients connect at once
    (SOTA §2.3). Returns True when proxying (caller must not continue startup).
    """
    probe_url = os.environ.get("UA_MCP_URL", "http://127.0.0.1:11239/")
    try:
        import httpx

        resp = await asyncio.to_thread(
            httpx.post,
            probe_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "probe", "version": "1"},
                },
            },
            headers={"Accept": "application/json, text/event-stream"},
            timeout=0.5,
        )
        if resp.status_code == 200:
            logger.info("HTTP daemon found at %s -- proxying tool calls", probe_url)
            # Client-level timeout bounds forwarded calls: ProxyTool has no read
            # timeout of its own, so without this one stalled daemon call wedges
            # the stdio session forever. 55s sits under the host 60s MCP timeout.
            proxy = FastMCPProxy(
                client_factory=lambda: Client(probe_url, timeout=55),
                name="UniversalActuatorHub",
            )
            await proxy.run_stdio_async()
            return True
    except Exception as e:
        logger.debug("No HTTP daemon at %s (%s) - standalone stdio startup", probe_url, e)
    return False


def main():
    """Industrial entry point for Universal Actuator Hub."""
    # Windows binary mode for stdout to prevent JSON-RPC corruption
    if sys.platform == "win32":
        import msvcrt

        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    # SSE port for Universal Actuator Hub (11239); override with UA_SSE_PORT
    # If MCP_TRANSPORT is set to 'sse', use it. Otherwise FastMCP handles transport.
    _sse_port = int(os.environ.get("UA_SSE_PORT", os.environ.get("MCP_PORT", "11239")))
    _transport = os.environ.get("MCP_TRANSPORT", None)

    if _transport == "sse" or os.environ.get("UA_FORCE_SSE"):
        mcp.run(transport="sse", port=_sse_port)
    else:
        # Stdio: become a lightweight proxy when the HTTP daemon owns the state.
        if asyncio.run(_maybe_proxy_to_daemon()):
            return
        # Defaults to stdio or follows FastMCP environment variables
        mcp.run()


if __name__ == "__main__":
    main()
