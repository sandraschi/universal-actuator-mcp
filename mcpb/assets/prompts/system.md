# Universal Actuator Hub — MCP Server Capabilities

## Server Overview — Industrial Federation Gateway v2.1.0

The Universal Actuator Hub is a **federation gateway** that orchestrates discovery, search, and RAG indexing across the entire MCP fleet. It does not own media content directly — instead it connects to Calibre (port 10720), Plex (port 10740), Immich (port 10839), Docs MCP (port 10795), and Knowledge/Advanced Memory (port 10732) via their MCP tool interfaces. It aggregates results from all sub-servers into unified responses, manages a 384-dim LanceDB vector index for semantic cross-fleet search, and provides an autonomous agentic workflow engine that uses `ctx.sample()` for Plan-Execute-Audit cycles.

The server listens on port **10745** by default (configurable via `UA_SSE_PORT` or `MCP_PORT`). It exposes 14 MCP tools, 9 REST endpoints, and an in-memory activity log ring buffer (2000 entries, queryable via `/api/logs`). CORS is configured for localhost, Tauri WebView (`tauri://localhost`, `http://tauri.localhost`, `https://tauri.localhost`), Tailscale `*.ts.net` domains, LAN IP ranges (`192.168.x.x`, `10.x.x.x`), CGNAT (`100.x.x.x`), and localhost variants.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│               Universal Actuator Hub                     │
│                      Port 10745                           │
│                                                          │
│  ┌────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │  FastMCP    │  │  REST API      │  │  Agentic        │ │
│  │  14 Tools   │  │  9 Endpoints   │  │  Workflow       │ │
│  └─────┬───────┘  └───────┬────────┘  │  Engine         │ │
│        │                  │            └───────┬────────┘ │
│  ┌─────┴──────────────────┴────────────────────┴──────┐  │
│  │            FleetManager + FleetAggregator            │  │
│  │  (MCP Client Sessions to sub-servers via stdio/SSE) │  │
│  └─────┬──────────────────┬──────────────────┬──────────┘  │
│        │                  │                  │              │
│  ┌─────┴─────┐    ┌──────┴──────┐    ┌──────┴──────┐      │
│  │  LanceDB   │    │  Activity   │    │  Milestones  │      │
│  │  RAG (384) │    │  Log Buffer │    │  JSON File   │      │
│  └───────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
  │  Calibre  │ │   Plex   │ │  Immich  │ │  Docs/Knowledge│
  │ :10720    │ │ :10740   │ │ :10839   │ │  :10795/:10732│
  └──────────┘ └──────────┘ └──────────┘ └──────────────┘
```

### Federation Architecture

The `FleetManager` (defined in `src/universal_actuator_mcp/fleet.py`) reads sub-server configurations from `config.json` at the repo root. The `servers` key defines each sub-server with its command, args, PYTHONPATH, and optional `scheme`/`url` for SSE transport. The `FleetAggregator` (in `fleet_aggregator.py`) connects to each sub-server using the MCP Python SDK (`mcp.ClientSession`), either via stdio subprocess or SSE client. Connection is lazy — sessions are established on demand and cached for reuse. At startup, the lifespan handler calls `ensure_all()` which probes each SSE-configured node's port and starts it if offline (spawns `uv run -m module` with `MCP_TRANSPORT=http` and `MCP_PORT=<port>`).

The federated search fan-out (`aggregate_search`) dispatches parallel MCP tool calls to all five nodes:
- **Calibre**: calls `query_books({operation: "search"|"recent", query, limit})`
- **Plex**: calls `plex_search({query, limit})`
- **Immich**: calls `search_photos({query, limit})`
- **Docs (mcp-central-docs)**: calls `search_docs({query, limit})`
- **Knowledge (advanced-memory-mcp)**: calls `adn_knowledge({operation: "search", query, page, results_per_page})`

Each node's raw results are normalised through format-specific formatters that produce a standard schema: `{title, author, source, type, id, metadata}`.

### LanceDB RAG Engine

The `LanceDBRag` class (in `src/universal_actuator_mcp/rag.py`) manages a LanceDB vector index stored at `backend/state/lancedb/`. It uses **384-dimensional embeddings** — either from `sentence-transformers/all-MiniLM-L6-v2` (when installed) or a deterministic MD5-based hash-embedding fallback. The table schema stores: `id`, `title`, `author`, `source`, `item_type`, `metadata_json`, and a 384-dim `vector` column.

On ingest, each item is concatenated (title + author + source + type) and embedded text is used for vector search. Semantic search returns results with a `_score` field (lower = more similar). Optional `source` filter restricts results to "calibre", "plex", or "immich". The index population happens via `ingest_fleet_to_rag()` which fetches up to 500 items per source from all five nodes and batch-inserts them.

### Activity Log Ring Buffer

An in-memory `deque(maxlen=2000)` stores structured log entries with `id` (timestamp-nanosecond + uuid6), `timestamp`, `level`, `kind`, `detail`, and `meta`. Queryable via REST at `/api/logs` with filters for level (DEBUG/INFO/WARNING/ERROR), kind, search text, sort order, pagination, and `after_id` (for polling). Stats available at `/api/logs/stats`. Clearable via `/api/logs/clear`.

### Configuration

Primary data source: `config.json` in the repo root (reads from `src/universal_actuator_mcp/fleet.py` parent dir). The `servers` object defines MCP sub-server entries. Default entries include: files, system, browser, blender, gimp, inkscape, knowledge (SSE :10732), infrastructure, devices, plex (SSE :10740), calibre (SSE :10720), robotics, meta, immich (SSE :10839), docsops (SSE :10795), consumption.

SSE-configured nodes (`url` + `"scheme": "sse"`) are auto-started by the lifespan handler: if their port is closed, the manager spawns `uv run -m <module>` with `MCP_TRANSPORT=http` and `MCP_PORT=<port>`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UA_SSE_PORT` | `10745` | SSE transport port for the hub itself |
| `MCP_PORT` | `10745` | Fallback port when UA_SSE_PORT is not set |
| `MCP_TRANSPORT` | (none) | Set to `"sse"` to force SSE transport mode |
| `UA_FORCE_SSE` | (none) | Any truthy value forces SSE transport |
| `CONFIG_PATH` | `config.json` | Alternative config file path |

---

## Tools

### 1. universal_actuator

**Signature:** `universal_actuator(domain: str, action: str, payload: dict[str, Any], ctx: Context) -> dict[str, Any]`

Portmanteau tool that routes to domain-specific subsystems. Reduces semantic overhead by consolidating cross-domain actions into a single call.

**Operations:**

| domain | action | payload keys | Behaviour |
|--------|--------|-------------|-----------|
| `"media"` | `"search"` | `query`, `domain` | Delegates to `search_federated` (federated search across fleet) |
| `"media"` | `"ingest"` | (ignored) | Delegates to `ingest_fleet_to_rag` |
| `"media"` | `"rag_search"` | `query`, `limit`, `source` | Delegates to `rag_semantic_search` |
| `"system"` | `"telemetry"` | (ignored) | Delegates to `get_fleet_telemetry` |
| `"system"` | `"discover"` | (ignored) | Delegates to `glom_on` |
| `"system"` | `"models"` | (ignored) | Delegates to `list_ollama_models` |

**Route fallback:** Any unrecognised domain/action pair returns `{"status": "partial_success", "message": "Domain 'X' action 'Y' routed via fallback.", "routing_key": "X.Y"}`.

**Return format:**
```json
{
  "status": "success|partial_success",
  "message": "Human-readable summary",
  "routing_key": "media.search",
  "results": { ... }
}
```

### 2. universal_status

**Signature:** `universal_status(ctx: Context) -> dict[str, Any]`

Aggregated health dashboard. Returns fleet telemetry (active nodes, host CPU/RAM), RAG index stats (total items, embedding model), and system version info.

**Return format:**
```json
{
  "fleet": {
    "fleet_status": "Healthy|Standalone",
    "active_nodes": 3,
    "total_discovered": 12,
    "host_metrics": {"cpu_percent": 23.4, "memory_percent": 62.1, "available_gb": 14.2},
    "node_details": [{"name": "calibre", "port": 10720, "status": "online", "source": "..."}]
  },
  "rag": {
    "initialized": true,
    "total_items": 1250,
    "embedding_model": "all-MiniLM-L6-v2",
    "source_distribution": {"calibre": 500, "plex": 300, "immich": 200, "docsops": 150, "knowledge": 100}
  },
  "system": {"version": "2.1.0", "mcp_version": "3.2.0", "timestamp": "2026-07-14T..."}
}
```

### 3. search_federated

**Signature:** `search_federated(query: str, ctx: Context, domain: str = "all") -> dict[str, Any]`

Parallel fan-out search across connected fleet nodes. The `domain` parameter selects which subset of nodes to query. Calls each sub-server's search tool concurrently via `asyncio.gather` and normalises results into a unified schema.

**Domain options:**
- `"all"` — queries all five nodes (Calibre, Plex, Immich, Docs, Knowledge)
- `"calibre"` — queries only Calibre (`query_books` on port 10720)
- `"plex"` — queries only Plex (`plex_search` on port 10740)
- `"immich"` — queries only Immich (`search_photos` on port 10839)
- `"docs"` / `"docsops"` — queries only Docs MCP (`search_docs` on port 10795)
- `"knowledge"` / `"memory"` — queries only Advanced Memory (`adn_knowledge` on port 10732)

**Return format:**
```json
{
  "query": "neural networks",
  "domain": "all",
  "results": {
    "calibre": [{"title": "...", "author": "...", "source": "calibre", "type": "book", "id": "42", "metadata": {...}}],
    "plex": [],
    "immich": [],
    "docsops": [],
    "knowledge": []
  },
  "total_hits": 5,
  "timestamp": "2026-07-14T..."
}
```

**Error handling:** Failed node connections are logged and return empty lists — they do not block results from other nodes.

### 4. rag_semantic_search

**Signature:** `rag_semantic_search(query: str, ctx: Context, limit: int = 10, source: str | None = None) -> dict[str, Any]`

Vector similarity search over the LanceDB media index. Requires `ingest_fleet_to_rag()` to have been called at least once to populate the index. Uses either `all-MiniLM-L6-v2` (384-dim, via sentence-transformers) or a deterministic hash-embedding fallback.

**Parameters:**
- `query`: Natural language query string
- `limit`: Max results (default 10)
- `source`: Optional filter — `"calibre"`, `"plex"`, or `"immich"`

**Return format:**
```json
{
  "query": "sci-fi novels 2001",
  "source_filter": null,
  "results": [
    {"id": "123", "title": "Dune", "author": "Frank Herbert", "source": "calibre", "type": "book", "metadata": {"series": "Dune", "tags": ["sci-fi"]}, "_score": 0.312}
  ],
  "result_count": 5,
  "index_size": 1250,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### 5. ingest_fleet_to_rag

**Signature:** `ingest_fleet_to_rag(ctx: Context) -> dict[str, Any]`

Bulk-ingest metadata from all five fleet nodes into the LanceDB RAG index. Fetches up to 500 items per source. Each item is embedded (384-dim) and upserted by ID. Safe to call repeatedly — existing items are overwritten.

**Return format:**
```json
{
  "ingested_per_source": {"calibre": 450, "plex": 320, "immich": 180, "docsops": 120, "knowledge": 90},
  "total_ingested": 1160,
  "rag_stats": {"initialized": true, "total_items": 1160, "embedding_model": "all-MiniLM-L6-v2", "source_distribution": {...}},
  "timestamp": "2026-07-14T..."
}
```

### 6. rag_stats

**Signature:** `rag_stats(ctx: Context) -> dict[str, Any]`

Return LanceDB RAG index statistics without performing a search.

**Return format:**
```json
{
  "initialized": true,
  "total_items": 1250,
  "embedding_model": "all-MiniLM-L6-v2",
  "db_path": "D:\\Dev\\repos\\universal-actuator-mcp\\backend\\state\\lancedb",
  "source_distribution": {"calibre": 500, "plex": 300, "immich": 200, "docsops": 150, "knowledge": 100}
}
```

### 7. rag_clear

**Signature:** `rag_clear(ctx: Context) -> dict[str, Any]`

Drop and recreate the LanceDB RAG table, removing all indexed items. Use before a fresh ingest cycle.

**Return format:**
```json
{"status": "cleared", "timestamp": "2026-07-14T..."}
```

### 8. glom_on

**Signature:** `glom_on(ctx: Context) -> dict[str, Any]`

Auto-discovery of MCP servers. Reads MCP configuration files from standard IDE config paths (`%USERPROFILE%/.gemini/antigravity/mcp_config.json`, `%APPDATA%/Claude/claude_desktop_config.json`, `%APPDATA%/Windsurf/mcp_config.json`) and scans ports 10700-10900 for active TCP services.

**Config files scanned:**
- `~/.gemini/antigravity/mcp_config.json`
- `%APPDATA%/Claude/claude_desktop_config.json`
- `%APPDATA%/Windsurf/mcp_config.json`

**Return format:**
```json
{
  "discovered_servers": [
    {"name": "calibre", "source": "C:/Users/.../claude_desktop_config.json", "command": "python -m calibre_mcp.server", "active": true, "port": 10720}
  ],
  "count": 15,
  "active_count": 8,
  "active_ports": [10720, 10740, 10732, 10795, 10839, ...],
  "scan_range": "10700-10900",
  "timestamp": "2026-07-14T..."
}
```

### 9. get_fleet_telemetry

**Signature:** `get_fleet_telemetry(ctx: Context) -> dict[str, Any]`

Real-time host health and fleet node telemetry. Combines port scan discovery with `psutil` host metrics (CPU %, memory %, available GB).

**Return format:**
```json
{
  "fleet_status": "Healthy",
  "active_nodes": 5,
  "total_discovered": 15,
  "host_metrics": {"cpu_percent": 18.5, "memory_percent": 55.3, "available_gb": 18.7},
  "node_details": [
    {"name": "calibre", "port": 10720, "status": "online", "source": "C:/Users/.../claude_desktop_config.json"}
  ],
  "telemetry_timestamp": "2026-07-14T..."
}
```

### 10. universal_milestone

**Signature:** `universal_milestone(title: str, description: str, ctx: Context, kind: str = "info") -> dict[str, Any]`

Log a persistent milestone entry to `backend/state/milestones.json`. Milestones are durable across server restarts and can be retrieved with `get_milestones_history`.

**Parameters:**
- `title`: Short, descriptive milestone title
- `description`: Free-text body for the milestone entry
- `kind`: One of `"info"`, `"warning"`, or `"achievement"` (default `"info"`)

**Return format:**
```json
{
  "status": "recorded",
  "milestone": {"title": "RAG index populated", "description": "Ingested 1250 items from 5 sources", "type": "achievement", "timestamp": "2026-07-14T..."}
}
```

### 11. get_milestones_history

**Signature:** `get_milestones_history(ctx: Context) -> dict[str, Any]`

Retrieve all recorded milestones from the persistent JSON file. Returns them in chronological order with a count.

**Return format:**
```json
{
  "milestones": [
    {"title": "Hub started", "description": "Server v2.1.0 initialised", "type": "info", "timestamp": "2026-07-14T..."},
    {"title": "Fleet connected", "description": "5 nodes active", "type": "achievement", "timestamp": "2026-07-14T..."}
  ],
  "count": 2
}
```

### 12. list_ollama_models

**Signature:** `list_ollama_models(ctx: Context) -> list[str]`

Probe the local Ollama instance at `http://127.0.0.1:11434/api/tags` and return available model names. Falls back to `["llama3", "mistral"]` if Ollama is unreachable or returns no models.

**Return format:**
```json
["llama3:latest", "mistral:latest", "codellama:7b", "llama2-uncensored:latest"]
```

### 13. agentic_workflow_tool

**Signature:** `agentic_workflow_tool(goal: str, ctx: Context, max_steps: int = 5, context_depth: str = "comprehensive") -> dict[str, Any]`

Autonomous three-phase workflow engine per SEP-1577: **Plan → Execute → Audit**. Uses `ctx.sample()` (FastMCP 3.2+ sampling) for both planning and audit phases.

**Phase 1 — Plan:** Builds a context block from fleet telemetry and RAG stats (when `context_depth="comprehensive"`). Sends a structured prompt to the connected LLM requesting a JSON plan with step-by-step tool calls.

**Phase 2 — Execute:** Iterates through planned steps (capped at `max_steps`). For each step, dispatches the specified tool via `_dispatch_tool()`. Supports tools: `search_federated`, `rag_semantic_search`, `ingest_fleet_to_rag`, `glom_on`, `get_fleet_telemetry`, `rag_stats`, `rag_clear`, `universal_milestone`, `get_milestones_history`, `list_ollama_models`.

**Phase 3 — Audit:** Sends an audit prompt to the LLM with step outcomes and asks for quality assessment (achieved, quality, issues, next_steps).

**Parameters:**
- `goal`: Natural language goal description (e.g. "Research latest AI papers in Calibre and log key findings")
- `max_steps`: Maximum execution steps (default 5, max 50)
- `context_depth`: `"comprehensive"` (includes fleet + RAG context) or `"basic"` (minimal context)

**Return format:**
```json
{
  "goal": "Research latest AI papers...",
  "correlation_id": "abc123",
  "plan": {"steps": [...], "expected_outcome": "..."},
  "steps_taken": [
    {"step": {"step": 1, "tool": "search_federated", "args": {"query": "AI", "domain": "calibre"}, "rationale": "..."}, "result": "{...}", "status": "success"}
  ],
  "audit": {"achieved": true, "quality": "good", "issues": [], "next_steps": []},
  "steps_executed": 5,
  "steps_succeeded": 5,
  "timestamp": "2026-07-14T..."
}
```

**Error handling:** If `ctx.sample()` is not available (host doesn't support sampling), the plan defaults to a single-step fallback (get_fleet_telemetry). Step execution continues through failures, logging each error. Audit phase uses a fallback assessment when LLM audit is unavailable.

### 14. universal_shutdown

**Signature:** `universal_shutdown(ctx: Context) -> dict`

Gracefully shut down the Universal Actuator server. Calls `os._exit(0)` after logging the shutdown event. Irreversible — all in-memory state, fleet sessions, and RAG cache are lost.

**Return format:**
```json
{"success": true, "message": "Server shutting down."}
```

(Note: the process exits immediately after this response; no further tool calls will succeed.)

---

## REST API

All endpoints are served on the same port (10745) via the FastMCP HTTP app.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root health — service name, version, SOTA standard |
| GET | `/api/v1/health` | Detailed health with RAG stats |
| GET | `/api/v1/deps` | Dependency check — Calibre (:10720) and Plex (:10740) port probes |
| GET | `/health` | Alias for /api/v1/health |
| GET | `/api/v1/models` | List Ollama models (REST bridge) |
| GET | `/library?q=<query>&domain=<domain>` | Federated search flattened for frontend list-viewers |
| POST | `/library/ingest` | Trigger RAG ingest |
| GET | `/telemetry` | Fleet telemetry |
| GET | `/api/logs` | Query activity log (params: limit, offset, level, kind, search, sort, after_id) |
| GET | `/api/logs/stats` | Activity log statistics |
| POST | `/api/logs/clear` | Clear activity log |
| POST | `/chat` | Simple echo endpoint for chat bridge |
| POST | `/api/shutdown` | Shutdown the server |

## In-Memory Activity Log

The `ActivityLog` class uses `collections.deque(maxlen=2000)` to store structured entries. Each entry has: `id` (float-time.uuid6), `timestamp` (ISO 8601), `level` (DEBUG/INFO/WARNING/ERROR), `kind` (tool name or category), `detail` (message body), and `meta` (dict of ancillary data).

The REST query endpoint supports:
- `level` filter: DEBUG=0, INFO=1, WARNING=2, ERROR=3 (shows entries at or above the specified level)
- `kind` filter: exact match on the entry kind
- `search` filter: case-insensitive substring match on detail
- `sort`: `"desc"` (newest first, default) or `"asc"` (oldest first)
- `after_id`: timestamp-based cursor for incremental polling
- `limit`/`offset`: standard pagination

## Sub-Server Configuration

The `config.json` at the repo root defines MCP sub-servers under a `"servers"` key. Each entry specifies:

```json
{
  "servers": {
    "calibre": {
      "command": "python",
      "args": ["-m", "calibre_mcp.server"],
      "env": {"PYTHONPATH": "D:/Dev/repos/calibre-mcp/src"},
      "url": "127.0.0.1:10720",
      "scheme": "sse"
    }
  }
}
```

Nodes with `"scheme": "sse"` and a `"url"` are auto-started by the lifespan handler — if their port is unreachable, the manager spawns a headless process with `uv run -m` and environment variables `MCP_TRANSPORT=http`, `MCP_PORT=<port>`, `MCP_HOST=127.0.0.1`.

## CORS Configuration

The FastAPI app (`mcp.http_app()`) mounts `CORSMiddleware` with:
- `allow_origins`: `http://localhost:10745`, `http://localhost:10982`, `http://127.0.0.1:10745`, `http://127.0.0.1:10982`, `http://tauri.localhost`, `https://tauri.localhost`, `tauri://localhost`
- `allow_origin_regex`: Comprehensive regex covering Tailscale `*.ts.net` and `*.tail-*.ts.net` domains, `tauri.localhost`, localhost, 127.0.0.1, 192.168.x.x, 10.x.x.x, 100.x.x.x (Tailscale CGNAT) — all with optional port suffixes.
- `allow_credentials`: true
- `allow_methods`: `["*"]`
- `allow_headers`: `["*"]`

## Data Lifecycle

The Universal Actuator Hub manages three persistent data stores with different lifecycle characteristics:

**LanceDB Vector Index** (`backend/state/lancedb/`): Persists across restarts. Created on first `initialize()` call during server lifespan. Populated by `ingest_fleet_to_rag()` which fetches and embeds items from all connected fleet sources. Cleared by `rag_clear()` which drops and recreates the table. The index accumulates across multiple ingest calls — items with the same ID are overwritten. Recommended refresh cycle: clear and re-ingest when new content is added to Calibre, Plex, or Immich libraries.

**Milestones File** (`backend/state/milestones.json`): Simple JSON array persisted to disk. Appended to by `universal_milestone()`. Read in full by `get_milestones_history()`. There is no deletion or editing mechanism — milestones are an append-only log. Manually editable if you need to remove entries.

**Activity Log** (in-memory `deque`): Volatile — lost on server shutdown. Max 2000 entries. Old entries are evicted automatically when the buffer is full. Queryable via REST API with filters, pagination, and cursor-based polling (`after_id`). Designed for operational debugging within a single session, not long-term audit.

## Sub-Server Auto-Start (Headless Mode)

The lifespan handler's `ensure_all()` method scans all servers in `config.json` that have `"scheme": "sse"` and a `"url"` field. For each one, it probes the configured port. If the port is unreachable, it spawns a headless `uv run -m <module>` subprocess with the following environment:

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTHONPATH` | From config.json `env.PYTHONPATH` | Resolves Python imports |
| `MCP_TRANSPORT` | `http` | Forces HTTP transport mode |
| `MCP_PORT` | Port from config URL | Target port for the sub-server |
| `MCP_HOST` | `127.0.0.1` | Localhost binding |
| `PYTHONUNBUFFERED` | `1` | Prevents stdout buffering |

The process is spawned with `subprocess.Popen` and `CREATE_NO_WINDOW` flag (Windows) to prevent terminal popups. If the port does not open within 10 seconds, the start is reported as "starting" rather than "failed" — some servers take longer to initialise their database connections.

## Lifespan & Shutdown Sequence

**Startup** (in `@mcp.lifespan()`):
1. LanceDB RAG engine initialises (`await _rag.initialize()`)
2. FleetManager is created and reads `config.json`
3. `ensure_all()` probes all SSE-configured nodes and starts offline ones
4. Server opens MCP transport (stdio or SSE on port 10745)

**Runtime**:
- MCP tools process requests via the FastMCP event loop
- FleetAggregator maintains lazy MCP client sessions to sub-servers
- Activity log collects structured entries
- Milestones are appended to disk on each `universal_milestone()` call

**Shutdown** (in `@mcp.lifespan()` yield cleanup):
1. FleetManager closes all MCP client sessions (`await _fleet.close()`)
2. All spawned subprocesses receive `terminate()` signal
3. In-memory activity log is lost

**Emergency Shutdown** (`universal_shutdown()` tool or `POST /api/shutdown`):
1. Calls `os._exit(0)` immediately
2. Does NOT run the lifespan cleanup
3. Fleet subprocesses continue running (they become orphaned)

## LanceDB RAG Details

| Property | Value |
|----------|-------|
| Embedding dimension | 384 |
| Backend | LanceDB |
| Table name | `media_items` |
| Storage location | `backend/state/lancedb/` |
| Primary embedding | `sentence-transformers/all-MiniLM-L6-v2` |
| Fallback embedding | MD5-based deterministic hash |
| Schema | id (string), title (string), author (string), source (string), item_type (string), metadata_json (string), vector (384-dim float32 list) |
| Search mode | Cosine/dot-product similarity via LanceDB default |

## Data Lifecycle

1. **Startup**: LanceDB connects, FleetManager syncs config, `ensure_all()` probes and starts SSE nodes
2. **Ingest**: `ingest_fleet_to_rag()` fetches up to 500 items/source from all 5 nodes, embeds, and upserts to LanceDB
3. **Search**: `rag_semantic_search()` embeds the query, searches LanceDB by vector similarity, returns ranked results
4. **Milestone**: `universal_milestone()` appends to `backend/state/milestones.json` — persists across restarts
5. **Shutdown**: FleetManager closes all MCP sessions, subprocesses are terminated
