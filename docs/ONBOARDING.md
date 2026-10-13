# Onboarding — universal-actuator-mcp

Get from zero to a working federation hub in ~10 minutes.

## 1. Install

```powershell
git clone https://github.com/sandraschi/universal-actuator-mcp
cd universal-actuator-mcp
just bootstrap   # uv sync + pre-commit hook
```

Requires: Python 3.12+, `uv`, bun (frontend), Ollama optional (local LLM).

## 2. Start

```powershell
just serve
```

Backend: `http://127.0.0.1:11239` (`GET /health` → `{"status":"ok"}`).
Frontend: `cd webapp; bun run dev` → `http://127.0.0.1:11240`.

## 3. Connect your first node

1. Open the dashboard — the red onboarding banner points here.
2. Go to **Status**: `glom_on()` scans MCP configs + ports 10700-10900.
3. Go to **Library**: run an ingest so federated search has data.
4. Go to **Chat**: issue a cross-domain command.

## 4. Money / accounts

None. All local: LanceDB + sentence-transformers run on your machine.
Ollama is free and optional (fallbacks otherwise).

## 5. Pitfalls

- Ports **11239/11240 are non-adjacent** (registry history) — don't "fix" them locally.
- Never hardcode node URLs in the frontend; add backend proxy routes instead.
- `main.py` at repo root is a dead scaffold stub, not the entry (`server:main` is).

## 6. Sanity check

```powershell
Invoke-RestMethod http://127.0.0.1:11239/api/capabilities | ConvertTo-Json -Depth 3
```

Expect `tool_count: 14`.
