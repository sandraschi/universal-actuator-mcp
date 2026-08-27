# universal-actuator-mcp — Claude Code instructions

## Entry Points
- `uv run python -m universal_actuator_mcp.server` — starts hub
- `just lint` — ruff check
- `just test` — pytest
- `just dev` — uvicorn on port 10929

## Key Files
- `src/universal_actuator_mcp/server.py` — FastMCP server with 14 tools
- `src/universal_actuator_mcp/fleet.py` — FleetManager subprocess orchestration
- `src/universal_actuator_mcp/fleet_aggregator.py` — MCP ClientSession + parallel search
- `src/universal_actuator_mcp/rag.py` — LanceDB vector RAG
- `config.json` — federated sub-server definitions
- `webapp/` — React 19 + Vite frontend

## Standards
- Follow TOOL_DESIGN_STANDARDS.md
- CORS must include tauri://localhost origins
- .env.example (not .env) in tauri bundle resources

