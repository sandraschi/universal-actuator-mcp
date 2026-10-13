# Universal Actuator Hub — User Guide

## Introduction

The Universal Actuator Hub is your personal fleet operations centre. It connects to every MCP server in your ecosystem — Calibre (ebooks), Plex (movies/TV), Immich (photos), Docs (technical documentation), and Advanced Memory (knowledge notes) — and gives you a single tool to search, analyse, and orchestrate across all of them at once. Think of it as a universal remote for your MCP fleet.

This guide walks through real-world workflows step by step. Each tutorial starts with a plain-English goal and shows you exactly which tools to call and what to expect back.

---

## Tutorial 1: "What Can You Do?" — Taking Stock with universal_status

**Scenario:** You have just connected to the Universal Actuator Hub and want to understand what services are available, how many items are indexed in the RAG, and whether the host machine has enough resources for heavy work.

**Step 1: Check fleet health and RAG status**

Call `universal_status()` with no arguments:

```python
result = await universal_status()
```

**What you get back:**

The response has three sections. The `fleet` block tells you how many nodes are online and the host's CPU/memory load. The `rag` block shows how many items are in the vector index and which embedding engine is active. The `system` block confirms the software versions.

**Interpreting the response:**

- If `fleet_status` is `"Healthy"`, most of your connected services are reachable. If `"Standalone"`, the hub cannot reach any sub-servers — check if Calibre/Plex/Immich are running.
- If `rag.total_items` is 0, you need to run `ingest_fleet_to_rag()` before semantic search will return results.
- If `host_metrics.available_gb` is below 2 GB, consider closing other applications before running resource-heavy workflows like `agentic_workflow_tool`.

**Probing deeper:**

If the fleet status looks concerning, drill down with individual tools:

```python
# See which MCP servers are registered in config files
discovery = await glom_on()

# Check dependency ports directly
# Calibre should be on :10720, Plex on :10740
# You can see this in the REST API at GET /api/v1/deps
```

---

## Tutorial 2: "Search Everything for 'Neural Networks'" — Federated Search

**Scenario:** You are researching neural network architectures. You want to check your Calibre library for relevant ebooks, your Plex media server for documentary movies, your Immich photo library for conference slides, your documentation corpus for technical guides, and your knowledge notes for previous research — all in one query.

**Step 1: Search all domains at once**

Call `search_federated` with `domain="all"` (the default):

```python
results = await search_federated(
    query="neural networks",
    domain="all"
)
```

**What you get back:**

The response contains a `results` dictionary with keys for each source: `calibre`, `plex`, `immich`, `docsops`, and `knowledge`. Each list contains normalised items with `title`, `author`, `source`, `type`, `id`, and `metadata`.

A `total_hits` field tells you how many results were found across all sources. A typical response might show 3 books from Calibre (titles like "Deep Learning", "Neural Networks for Pattern Recognition"), 1 documentary from Plex ("The GPU Revolution"), and 2 documentation pages from Docs MCP.

**Step 2: Search a single domain**

If you only want to search your Calibre library, narrow the domain:

```python
calibre_only = await search_federated(
    query="transformer architecture",
    domain="calibre"
)
```

Available domains: `"all"`, `"calibre"`, `"plex"`, `"immich"`, `"docs"`, `"knowledge"`.

**Step 3: Use the portmanteau router**

The `universal_actuator` portmanteau also handles search, which is useful when you want to stay in a single routing paradigm:

```python
results = await universal_actuator(
    domain="media",
    action="search",
    payload={"query": "neural networks", "domain": "all"}
)
```

**Troubleshooting:**

- If a source returns an empty list, that sub-server may be offline. Check `GET /api/v1/deps` to see if Calibre (`:10720`) and Plex (`:10740`) are reachable.
- If all sources return empty, your config.json may not have the correct PYTHONPATH entries.
- The search sends empty-string queries as "list/recent" operations where supported — so `search_federated(query="")` acts as a "show me everything" on each source.

---

## Tutorial 3: "Summarise My Calibre Library into RAG" — Building the Vector Index

**Scenario:** You have thousands of ebooks in Calibre, movies in Plex, and photos in Immich. You want to expose all this metadata to semantic vector search so you can ask natural-language questions like "find me sci-fi novels from the 1990s" without writing precise search queries.

**Step 1: Check current RAG state**

Before ingesting, check if there is already data in the vector index:

```python
stats = await rag_stats()
```

If `total_items` is already high, you might want to clear and re-ingest:

```python
cleared = await rag_clear()
```

**Step 2: Run the ingest**

```python
result = await ingest_fleet_to_rag()
```

This fetches up to 500 items from each of the five sources (Calibre, Plex, Immich, Docs, Knowledge), embeds each item's title + author + source + type into a 384-dimensional vector, and upserts everything into the LanceDB table at `backend/state/lancedb/`.

**What you get back:**

```json
{
  "ingested_per_source": {"calibre": 450, "plex": 320, "immich": 180, "docsops": 120, "knowledge": 90},
  "total_ingested": 1160,
  "rag_stats": {
    "initialized": true,
    "total_items": 1160,
    "embedding_model": "all-MiniLM-L6-v2",
    "source_distribution": {"calibre": 450, "plex": 320, "immich": 180, "docsops": 120, "knowledge": 90}
  }
}
```

**Step 3: Search semantically**

Now you can query by meaning, not just keywords:

```python
results = await rag_semantic_search(
    query="sci-fi space exploration",
    limit=5
)
```

For a book titled "Dune" by Frank Herbert, the `_score` might be around 0.31 (lower = more similar). A Plex documentary about the James Webb Space Telescope might score around 0.45.

**Step 4: Filter by source**

If you only want results from your photo library:

```python
photos = await rag_semantic_search(
    query="conference presentation slides",
    limit=10,
    source="immich"
)
```

**Performance notes:**

- Ingesting 500 items per source = ~2500 total items. With sentence-transformers, this takes about 30-60 seconds. With hash-embedding fallback, it takes under 5 seconds but search quality is lower.
- The RAG index persists at `backend/state/lancedb/` across server restarts. You do not need to re-ingest every time you restart.
- Running `rag_clear()` followed by `ingest_fleet_to_rag()` is the recommended refresh cycle when new content is added to your Calibre/Plex/Immich libraries.

---

## Tutorial 4: "Plan a Research Workflow" — Autonomous Agentic Orchestration

**Scenario:** You want to research a topic across your entire fleet without manually calling each tool. The agentic workflow engine will plan, execute, and audit a multi-step research pipeline automatically.

**Step 1: Launch an autonomous workflow**

```python
result = await agentic_workflow_tool(
    goal="Search my Calibre library for books about reinforcement learning, check my Plex for related documentaries, log the findings as a milestone, and give me a summary.",
    max_steps=5,
    context_depth="comprehensive"
)
```

**What happens behind the scenes:**

**Phase 1 — Plan:** The engine calls `ctx.sample()` and sends a structured prompt to the connected LLM. The LLM receives context about the current fleet state (how many nodes are active, how many items are in the RAG index) and is asked to produce a JSON plan. A typical plan might look like:

```json
{
  "steps": [
    {"step": 1, "tool": "search_federated", "args": {"query": "reinforcement learning", "domain": "calibre"}, "rationale": "Find relevant ebooks in Calibre"},
    {"step": 2, "tool": "search_federated", "args": {"query": "reinforcement learning documentary", "domain": "plex"}, "rationale": "Find relevant documentaries in Plex"},
    {"step": 3, "tool": "universal_milestone", "args": {"title": "RL Research Roundup", "description": "Searched Calibre+Plex for RL content", "kind": "achievement"}, "rationale": "Log findings as a milestone"},
    {"step": 4, "tool": "get_fleet_telemetry", "args": {}, "rationale": "Check system health after search load"}
  ],
  "expected_outcome": "List of RL books, documentaries, milestone recorded, system health verified"
}
```

**Phase 2 — Execute:** Each step is executed in sequence via the `_dispatch_tool()` router. Step results are truncated to 800 characters for the audit.

**Phase 3 — Audit:** The engine sends another `ctx.sample()` prompt asking the LLM to assess whether the goal was achieved. The response includes `achieved`, `quality`, `issues`, and `next_steps`.

**The output:**

```json
{
  "goal": "Search my Calibre library for books about reinforcement learning...",
  "correlation_id": "a1b2c3d4e5f6",
  "plan": { "...": "..." },
  "steps_taken": [...],
  "audit": {"achieved": true, "quality": "good", "issues": [], "next_steps": ["Review found items in Calibre GUI"]},
  "steps_executed": 4,
  "steps_succeeded": 4
}
```

**Tips for good results:**

- Be specific in your goal. "Search for RL books and log milestones" works better than "do research".
- Use `context_depth="comprehensive"` so the planner knows what's in your fleet and RAG.
- If the plan looks wrong, check that your LLM (the one connected to the MCP host) has good reasoning capability — the plan quality depends on the sampling LLM.
- If `ctx.sample()` is not available (some MCP hosts do not support sampling), the engine falls back to a single-step plan that just runs `get_fleet_telemetry`.

---

## Tutorial 5: "Discover What's Running" — Server Glom and Telemetry

**Scenario:** You have many MCP servers running across different IDEs and configurations. You want a comprehensive map of what is active and what is available.

**Step 1: Glom onto running servers**

```python
discovery = await glom_on()
```

This reads three config files:
1. `~/.gemini/antigravity/mcp_config.json`
2. `%APPDATA%/Claude/claude_desktop_config.json`
3. `%APPDATA%/Windsurf/mcp_config.json`

It cross-references each discovered server name against a port scan of 10700-10900. If a server has a port number in its command string and that port is active, it is marked `active: true`. Services found on the port scan but not in any config file are labelled `"UnknownService@<port>"`.

**Step 2: Get live telemetry**

```python
telemetry = await get_fleet_telemetry()
```

This combines the discovery scan with `psutil` host metrics. It returns:
- `fleet_status`: `"Healthy"` if at least one node is active, else `"Standalone"`
- `active_nodes`: count of online nodes
- `host_metrics.cpu_percent`: current CPU utilisation
- `host_metrics.memory_percent`: current RAM utilisation
- `host_metrics.available_gb`: how much RAM is free

**Step 3: Check dependency ports directly**

Hit `GET /api/v1/deps` via REST to see whether Calibre (`:10720`) and Plex (`:10740`) are specifically reachable.

**Use case examples:**

- Before running a heavy ingest, check `available_gb`. If it is under 2 GB, consider closing browsers or IDEs.
- If `active_nodes` is 0 after running `glom_on()`, check whether your MCP config files exist and have valid JSON.
- If `discovery.count` is unexpectedly high, you may have stale processes from old IDE sessions holding ports.

---

## Tutorial 6: "Keep a Project Log" — Milestones as a Persistent Notebook

**Scenario:** You are working through a multi-day research project. You want to record checkpoints, decisions, and discoveries so you can review your progress later.

**Step 1: Record a milestone**

```python
m1 = await universal_milestone(
    title="Started RL Research Sprint",
    description="Initialized RAG index with 1160 items from 5 sources. Starting literature review.",
    kind="achievement"
)
```

**Step 2: Record progress during work**

```python
m2 = await universal_milestone(
    title="Found Key Papers",
    description="Searched federated: found 3 RL books in Calibre, 1 documentary in Plex.",
    kind="info"
)

m3 = await universal_milestone(
    title="RAG Re-indexed",
    description="Cleared and re-ingested RAG with new Calibre additions.",
    kind="info"
)
```

**Step 3: Review your timeline**

```python
history = await get_milestones_history()
```

This returns all milestones in chronological order. The count tells you how many entries exist.

**Milestone kinds:**

| kind | When to use |
|------|-------------|
| `"info"` | Default — general progress updates |
| `"warning"` | Problems encountered, degraded functionality |
| `"achievement"` | Major completions, milestones of significance |

**Persistence:**

Milestones are stored in `backend/state/milestones.json` at the repo root. The file is written with JSON pretty-print (2-space indent). It survives server restarts. You can also read or edit the file manually if needed — it is a simple array of objects.

---

## Tutorial 7: "Check Local LLM Availability" — Ollama Discovery

**Scenario:** You want to use a local LLM for summarisation tasks. The Hub can probe your local Ollama instance to see what models are available.

**Step 1: List available models**

```python
models = await list_ollama_models()
```

This queries `http://127.0.0.1:11434/api/tags` with a 2-second timeout.

**Step 2: Interpret results**

If Ollama is running, you get a list like:
```json
["llama3:latest", "mistral:latest", "codellama:7b", "llama2-uncensored:latest"]
```

If Ollama is not running, the tool returns sensible fallbacks: `["llama3", "mistral"]`. This is a graceful degradation — the agent can still suggest models even without an active Ollama connection.

**Step 3: Use in agentic workflows**

The `agentic_workflow_tool` can use discovered models for planning and audit phases via `ctx.sample()`. When the MCP host provides sampling, the workflow engine sends planning prompts and audit prompts through the host's LLM interface — which may route to Ollama if that is how the host is configured.

---

## Tutorial 8: "Shutdown When Done" — Clean Server Termination

**Scenario:** You have finished your work session and want to shut down the Hub cleanly.

**Step 1: Call the shutdown tool**

```python
shutdown = await universal_shutdown()
```

This returns `{"success": true, "message": "Server shutting down."}` and then calls `os._exit(0)`. The server process terminates immediately.

**What is lost:**

- In-memory activity log (2000 entries in the ring buffer)
- Active FleetAggregator sessions (MCP client connections to sub-servers)
- Sub-processes spawned by `ensure_all()` are NOT killed automatically — they will continue running as headless services

**What persists:**

- LanceDB RAG index at `backend/state/lancedb/` — survives restarts
- Milestones at `backend/state/milestones.json` — survives restarts
- `config.json` — the server reads it fresh on each start

**Alternative: REST shutdown**

You can also shut down via REST:
```
POST /api/shutdown
```

This is equivalent to the MCP tool call — same `os._exit(0)` behaviour.

---

## Tutorial 9: "Monitor the Activity Log" — Observability

**Scenario:** You want to see what the Hub has been doing — which tools were called, whether any errors occurred, and how the system is performing.

**Step 1: Query recent activity**

Hit `GET /api/logs?limit=20` via REST, or access the log data programmatically through the in-memory `ActivityLog` (there is no dedicated MCP tool for log query — use the REST API).

**Step 2: Filter by severity**

```
GET /api/logs?level=ERROR&limit=100
```
Returns all ERROR-level entries (up to 100).

```
GET /api/logs?level=WARNING&limit=50
```
Returns WARNING + ERROR entries (levels cascade: WARNING shows WARNING and ERROR).

**Step 3: Search for specific activity**

```
GET /api/logs?search=ingest&limit=20
```
Finds all log entries whose `detail` contains "ingest".

**Step 4: Poll for new entries**

```
GET /api/logs?after_id=1744567890.123456.a1b2c3&limit=10
```
Returns entries newer than the specified ID. Use this for incremental log polling.

**Step 5: Check aggregate stats**

```
GET /api/logs/stats
```
Returns total entries, max_entries, and breakdowns by level and kind.

**Step 6: Clear the log**

```
POST /api/logs/clear
```
Resets the ring buffer. Useful before starting a fresh session so you only see new activity.

---

## Tutorial 10: "Use the REST Bridge" — HTTP Access

**Scenario:** You have a webapp or script that needs to call the Hub over HTTP instead of MCP.

**Health check:**

```
GET http://localhost:10745/
```
Returns: `{"status": "online", "service": "Universal Actuator Hub", "version": "2.1.0"}`

**Dependency check:**

```
GET http://localhost:10745/api/v1/deps
```
Returns: `{"ok": true, "deps": {"calibre": {"port": 10720, "up": true}, "plex": {"port": 10740, "up": true}}}`

**Frontend library search (flattened):**

```
GET http://localhost:10745/library?q=dune&domain=calibre
```
Returns a flat `items` array — useful for list-viewer frontends that cannot handle nested source dicts.

**Trigger ingest from an external script:**

```
POST http://localhost:10745/library/ingest
```
Returns the same response as `ingest_fleet_to_rag()`.

**Get telemetry for a dashboard:**

```
GET http://localhost:10745/telemetry
```
Returns fleet status, node details, and host metrics.

**List Ollama models:**

```
GET http://localhost:10745/api/v1/models
```
Returns `{"models": ["llama3:latest", ...]}`

**Send a chat message:**

```
POST http://localhost:10745/chat
Content-Type: application/json

{"message": "What's the fleet status?"}
```
Returns a simple echo acknowledgment.

---

## Tutorial 11: "Connect via the Portmanteau Router" — Universal Actuator Patterns

**Scenario:** You prefer a single entry point for all operations rather than calling individual tools. The `universal_actuator` portmanteau consolidates the most common operations.

**Media search pattern:**
```python
await universal_actuator(
    domain="media",
    action="search",
    payload={"query": "genetic algorithms", "domain": "all"}
)
```

**Media ingest pattern:**
```python
await universal_actuator(
    domain="media",
    action="ingest",
    payload={}
)
```

**RAG semantic search pattern:**
```python
await universal_actuator(
    domain="media",
    action="rag_search",
    payload={"query": "deep reinforcement learning", "limit": 5}
)
```

**System telemetry pattern:**
```python
await universal_actuator(
    domain="system",
    action="telemetry",
    payload={}
)
```

**System discovery pattern:**
```python
await universal_actuator(
    domain="system",
    action="discover",
    payload={}
)
```

**System models pattern:**
```python
await universal_actuator(
    domain="system",
    action="models",
    payload={}
)
```

**Note on fallback routing:** Any domain/action combination that does not match the defined routes returns `{"status": "partial_success", "message": "Domain 'X' action 'Y' routed via fallback."}`. The tool never errors on unrecognised routes — it always returns a graceful response.

---

## Tutorial 12: "Maintenance Workflows" — Clear, Re-ingest, Verify

**Monthly maintenance checklist:**

**Step 1: Clear the old RAG index**
```python
await rag_clear()
```

**Step 2: Re-ingest from all sources**
```python
result = await ingest_fleet_to_rag()
```

**Step 3: Verify the index**
```python
stats = await rag_stats()
# Check total_items, source_distribution, embedding_model
```

**Step 4: Record the maintenance event**
```python
await universal_milestone(
    title="Monthly RAG Maintenance",
    description=f"Re-indexed {stats['total_items']} items from {len(stats['source_distribution'])} sources.",
    kind="achievement"
)
```

**Step 5: Verify search quality**
```python
test = await rag_semantic_search(
    query="sci-fi",
    limit=3,
    source="calibre"
)
```

---

## Troubleshooting Guide

**Problem: Fleet status shows "Standalone" even when services are running**
- Check that `config.json` exists at the repo root with valid JSON
- Verify the `servers` key exists (not `mcpServers` — FleetConfigManager reads `servers`)
- Ensure PYTHONPATH entries in config.json point to real directories
- Check if SSE nodes are actually listening: `netstat -an | findstr :10720`

**Problem: RAG search returns empty results**
- Run `rag_stats()` first — if `total_items` is 0, you need to run `ingest_fleet_to_rag()`
- If `embedding_model` is "hash-fallback", install sentence-transformers for better results: `pip install sentence-transformers`
- Check that the query is not overly specific — try shorter terms

**Problem: Ingest returns 0 items from all sources**
- The config.json may be missing or malformed. Check `backend/state/` for error logs.
- The sub-server ports may not be reachable. Hit `GET /api/v1/deps` to test Calibre and Plex connectivity.
- Each sub-server's search tool expects specific parameters. If a sub-server returns data for direct calls but not through the Hub, the FleetManager's tool-calling parameters may need adjustment.

**Problem: agentic_workflow_tool returns fallback plan**
- Your MCP host may not support `ctx.sample()`. Check if your client advertises sampling capabilities.
- The LLM response may not parse as valid JSON. The plan parsing handles markdown fences (```json) but structural errors in the JSON will trigger the fallback.
- Try simplifying the goal — shorter, more specific goals produce more reliable plans.

**Problem: Port 10745 is already in use**
- Set `UA_SSE_PORT` to an alternate port: `$env:UA_SSE_PORT = "10755"`
- Kill the existing process: `Get-NetTCPConnection -LocalPort 10745 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`

**Problem: CORS errors when connecting from a webapp**
- The allowed origins include localhost:10745, localhost:11240, tauri://localhost, and Tailscale domains. If your webapp runs on a different port, add it to the `allow_origins` list in server.py.
- The `allow_origin_regex` covers `*.ts.net`, `192.168.x.x`, `10.x.x.x`, and `100.x.x.x` — Tailscale users on any of these subnets should work without modification.

---

## Tutorial 13: "Work with Multiple Users" — Session Isolation

**Scenario:** You are running a shared fleet and want to understand how session data is isolated between different users or different client connections.

**Key concepts:**

The Universal Actuator Hub uses FastMCP 3.2's correlation ID system (`ctx.correlation_id`) to trace individual tool calls. Each MCP session gets a unique correlation ID that appears in the activity log and in log output. This allows you to distinguish between different clients' requests even though they share the same server process.

**Session-scoped data:**

- The LanceDB RAG index is global — all clients share the same vector index. If one client calls `rag_clear()`, all clients lose the index.
- Milestones are global — stored in a single file on disk. All clients see all milestones.
- The activity log is global — entries from all clients are mixed by timestamp.
- FleetManager sessions are global — all clients trigger the same sub-server connections.

**Isolation via separate instances:**

If you need true multi-user isolation, run separate Hub instances on different ports:

```bash
# Instance 1 (user A)
$env:UA_SSE_PORT = "10745"
uv run python -m universal_actuator_mcp.server

# Instance 2 (user B) — different config.json
$env:UA_SSE_PORT = "10755"
$env:CONFIG_PATH = "config_user_b.json"
uv run python -m universal_actuator_mcp.server
```

Each instance has its own RAG index (`backend/state/lancedb/` — or override via LanceDBRag db_path) and its own milestones file.

## Tutorial 14: "Performance Tuning" — When to Call Each Tool

**Scenario:** Some operations are expensive (network I/O, embedding computation, parallel tool dispatch). Understanding the cost profile helps you choose the right tool for the job.

**Cost table (approximate, localhost):**

| Operation | Latency | Network I/O | Notes |
|-----------|---------|-------------|-------|
| `rag_stats()` | < 10 ms | None | Pure local query |
| `universal_milestone()` | < 10 ms | None | File append only |
| `get_milestones_history()` | < 10 ms | None | File read only |
| `list_ollama_models()` | ~ 50-200 ms | 1 HTTP call to :11434 | Depends on Ollama response time |
| `get_fleet_telemetry()` | ~ 500-2000 ms | Port scan 201 ports | Timeout-limited scan |
| `glom_on()` | ~ 500-2000 ms | File reads + port scan | Same as telemetry + config parsing |
| `rag_semantic_search()` | ~ 20-500 ms | None (local LanceDB) | Depends on sentence-transformers model load |
| `rag_clear()` | ~ 50-200 ms | None | LanceDB table drop + recreate |
| `search_federated(query="")` | ~ 1000-5000 ms | 5 parallel MCP tool calls | Empty query = list operation on each node |
| `search_federated(query="term")` | ~ 1000-5000 ms | 5 parallel MCP tool calls | Actual search on each node |
| `ingest_fleet_to_rag()` | ~ 30-120 s | 5 x 500 items + embeddings | Heaviest operation — embedding is CPU/GPU-bound |
| `agentic_workflow_tool()` | ~ 5-60 s per step | Variable | Depends on LLM sampling + tool dispatch |

**Guidelines:**

- For quick status checks, use `rag_stats()` or `get_fleet_telemetry()` — both return in milliseconds.
- For content discovery, prefer `rag_semantic_search()` over `search_federated()` when the RAG index is fresh — it is faster and does not require sub-server connectivity.
- Run `ingest_fleet_to_rag()` as a background maintenance task, not during interactive use. It can take over a minute.
- Empty-string `search_federated(query="")` is useful as a "show me everything" shortcut but does trigger network calls to all five sub-servers.

---

## Tutorial 15: "Tag and Track Your Work" — Milestone-Driven Development

**Scenario:** You are using the Hub daily and want to build a persistent log of what you have accomplished for weekly reviews and handovers.

**The milestone pattern:**

```python
# At the start of a session:
await universal_milestone(
    title="Session Start",
    description="Hub initialised, RAG index at 1160 items, 5 fleet nodes active.",
    kind="info"
)

# After a major operation:
result = await ingest_fleet_to_rag()
await universal_milestone(
    title="RAG Refresh Complete",
    description=f"Ingested {result['total_ingested']} new items from fleet sources.",
    kind="achievement"
)

# When something goes wrong:
await universal_milestone(
    title="Plex Connection Lost",
    description="Plex MCP server unreachable on port 10740. Federated search degraded.",
    kind="warning"
)

# At session end:
await universal_milestone(
    title="Session Summary",
    description=f"Completed {len(history['milestones'])} milestones. RAG index at {stats['total_items']} items.",
    kind="info"
)
```

**Reviewing your log:**

```python
# Before a weekly review:
history = await get_milestones_history()
achievements = [m for m in history["milestones"] if m["type"] == "achievement"]
warnings = [m for m in history["milestones"] if m["type"] == "warning"]
print(f"Weekly review: {len(achievements)} achievements, {len(warnings)} warnings")
```

**Suggested milestone convention:**

Each session should record at least three milestones: start, key operation(s), and end. The "achievement" type should be reserved for substantive completions (ingest complete, research sprint done, configuration migrated). Use "warning" for any degraded state — this makes weekly reviews more actionable when you can see at a glance which days had connectivity issues.

---

## FAQ

**Q: Do I need sentence-transformers installed?**
A: No. The Hub falls back to deterministic hash-embeddings if sentence-transformers is not available. Search still works — results just rely on lexical proximity rather than semantic understanding. For best results, install sentence-transformers: `pip install sentence-transformers`.

**Q: How many items can the RAG index hold?**
A: LanceDB has no hard limit. With 384-dim vectors, expect roughly 100,000 items per GB of disk. The Hub fetches up to 500 items per source per ingest call, which limits a single ingest to ~2500 items. You can call `ingest_fleet_to_rag()` multiple times.

**Q: Does the RAG index persist across server restarts?**
A: Yes. The LanceDB database at `backend/state/lancedb/` persists between restarts. Only call `ingest_fleet_to_rag()` when you add new content to your libraries.

**Q: Can I use the Hub without Calibre or Plex installed?**
A: Yes. The Hub degrades gracefully. If a sub-server is unreachable, its results section in federated search returns an empty list. Dependency checks report individual service status without blocking overall operation.

**Q: What is the default port and how do I change it?**
A: The default port is 10745. Set `UA_SSE_PORT` or `MCP_PORT` environment variable to change it. The main entry point (`server.py:main()`) reads these in order: `UA_SSE_PORT`, then `MCP_PORT`, then defaults to 10745.

**Q: Does the Hub support stdio transport?**
A: Yes. By default, `mcp.run()` starts in stdio mode (no env vars set). Set `MCP_TRANSPORT=sse` or `UA_FORCE_SSE=1` to switch to SSE mode on the configured port.

**Q: Can I add custom sub-servers to the federation?**
A: Yes. Add an entry to the `"servers"` object in `config.json` with `command`, `args`, and `env` fields. If the server supports SSE, add `"scheme": "sse"` and `"url": "127.0.0.1:<port>"` for auto-start. The aggregator will discover and connect to it on next restart.
