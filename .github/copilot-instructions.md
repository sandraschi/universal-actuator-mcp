# Universal Actuator MCP — Copilot instructions

Federation gateway: 14 MCP tools for cross-domain search, RAG, telemetry and agentic workflows.

Before starting work: check `universal_status()`, then `search_federated(query="...")`.
At end of work: record `universal_milestone(title="...", description="...")`.

Key files: `src/universal_actuator_mcp/server.py` (tools + REST), `webapp/src/` (dashboard),
`native/` (Tauri). Ports: backend 10929, frontend 10982.
