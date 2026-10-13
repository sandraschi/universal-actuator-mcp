# Development — universal-actuator-mcp

## Setup

```powershell
uv sync --group dev
just bootstrap        # dev deps + pre-commit hook
```

## Run

```powershell
just serve            # backend on :10929 (stdio for Claude Desktop by default)
just ci               # full local gates: ruff, format-check, pytest, tsc
```

Frontend lives in `webapp/` (bun: `bun install`, `bun run dev` on :10982).

## Gates

- Python: `uv run ruff check src/` + `uv run ruff format src/ --check` (T20 enforced, no S110/S112 ignores)
- Tests: `uv run pytest tests/ -q` (34 tests)
- Web: `bun run biome:ci` + `npx tsc --noEmit` in `webapp/`
- CI: `.github/workflows/ci.yml` (windows-latest) mirrors `just ci` + build

## Layout

- `src/universal_actuator_mcp/server.py` — 14 MCP tools + REST routes (capabilities, skills,
  llm/chat proxy, diagnostics, fleet proxy, shutdown)
- `src/universal_actuator_mcp/fleet.py` — headless node lifecycle
- `src/universal_actuator_mcp/rag.py` — LanceDB vector index
- `native/` — Tauri shell (`backend.rs`: free_port, stream watch, backend-status emit)
