# Configuration — universal-actuator-mcp

| Variable | Default | Purpose |
|---|---|---|
| `UA_SSE_PORT` / `MCP_PORT` | `10929` | HTTP/SSE backend port (registry: `WEBAPP_PORTS.md`) |
| `MCP_TRANSPORT` | unset (stdio) | Set `sse` to serve HTTP instead of stdio |
| `UA_FORCE_SSE` | unset | Force SSE even without `MCP_TRANSPORT=sse` |
| `FLEET_NODE_URL` | `http://127.0.0.1:10854` | Federated node registry proxied by `GET /api/fleet/servers` |
| `UA_MCP_URL` | `http://127.0.0.1:10929/` | Stdio probe target: when a daemon answers MCP `initialize` here, stdio becomes a proxy (55s fwd timeout) |
| `UA_PREFAB_APPS` | `1` | Set `0` to skip Prefab card registration (headless CI) |
| `VITE_API_BASE` | `""` (Vite proxy) | Set by `native/build.ps1` for Tauri installer builds only |
| `VITE_PORT` / `VITE_API_TARGET` | `10982` / backend | Frontend dev server (see `fleet-start.config.ps1`) |

Copy `.env.example` to `.env` for local overrides. Never commit `.env`.
Ports: backend **10929**, frontend **10982** (non-adjacent by registry history:
backend moved off the 10745 openclaw-molt collision).
