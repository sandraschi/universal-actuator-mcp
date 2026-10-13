# Tools — universal-actuator-mcp (14 MCP tools)

All tools use `Annotated[...]` params, `## Return Format` + `## Examples` docstrings.

| Tool | Purpose |
|---|---|
| `universal_actuator(domain, action, payload)` | Portmanteau router: media search/ingest/rag_search, system telemetry/discover/models |
| `universal_status()` | Health dashboard: fleet + RAG + version |
| `search_federated(query, domain)` | Fan-out search: calibre/plex/immich/docs/knowledge/all |
| `rag_semantic_search(query, limit, source)` | LanceDB vector search (call `ingest_fleet_to_rag` first) |
| `ingest_fleet_to_rag()` | Bulk ingest (500/source) into LanceDB |
| `rag_stats()` / `rag_clear()` | Index stats / full reset |
| `glom_on()` | Discover nodes: MCP configs + port scan 10700-10900 |
| `get_fleet_telemetry()` | CPU/RAM + node online/offline |
| `universal_milestone(title, description, kind)` | Persist milestone to `backend/state/milestones.json` |
| `get_milestones_history()` | Milestone timeline |
| `list_ollama_models()` | Live Ollama models (fallbacks when unreachable) |
| `agentic_workflow_tool(goal, max_steps)` | SEP-1577 plan → execute → audit via `ctx.sample()` |
| `universal_shutdown()` | Graceful termination |

## REST (same-origin via Vite proxy)

`GET /api/capabilities`, `GET /api/skills`, `GET /api/v1/health`, `GET /health`,
`GET /api/v1/models`, `POST /api/llm/chat` + `POST /api/llm/chat/stream` (backend proxy —
the only path Chat uses), `GET /api/v1/diagnostics`, `GET /api/fleet/servers`,
`GET /telemetry`, `GET/POST /library`, `POST /chat` (legacy alias), `POST /api/shutdown`
(responds 200, exits ~500 ms later).
