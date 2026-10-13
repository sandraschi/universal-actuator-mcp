# universal-actuator-mcp Agent Context

Fleet MCP server. See `justfile` for available recipes.

## Quick Ref

```powershell
uv run pytest tests/ -q
```

## HTTP Daemon + Stdio Proxy

- Daemon port: **10929** (`GET /health` → `{"status":"ok"}`); frontend :10982 (Vite proxy).
- Entry: `server:main` — stdio for Claude Desktop, SSE/HTTP when `MCP_TRANSPORT=sse`.
- State: LanceDB RAG + `backend/state/milestones.json` (no NSSM service; stdio-proxy
  migration per SOTA §2.3 is deferred — see CHANGELOG).
- Probe env: `UA_SSE_PORT` / `MCP_PORT` override the port; `FLEET_NODE_URL` sets the
  node registry behind `GET /api/fleet/servers`.
- Never run two daemons: `start.ps1` (fleet engine) owns zombie-clearing; don't
  hand-start uvicorn alongside it.
