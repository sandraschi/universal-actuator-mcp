# Troubleshooting — universal-actuator-mcp

## Backend won't start / port busy

`start.ps1` clears zombies via the fleet engine. Manual: check `:11239`
with `GET /health` — expect `{"status":"ok"}`.

## Dashboard shows OFFLINE

The frontend calls same-origin `/api/...` through the Vite proxy. A localhost-200
in curl proves nothing about a LAN/Tailscale tab: never hardcode backend URLs in
`webapp/src` (incident class: tools.tsx `:10854`, fixed 2026-10-13 via
`GET /api/fleet/servers` proxy).

## RAG returns nothing

Call `ingest_fleet_to_rag()` first. Check `rag_stats()` → `total_items > 0`.
`rag_clear()` wipes the LanceDB index for a fresh ingest.

## Ollama models fall back to llama3/mistral

`list_ollama_models()` returns SOTA fallbacks when `127.0.0.1:11434` is unreachable.
Start Ollama to get the live list.

## Tauri webview blocked

`native/tauri.conf.json` CSP allows `127.0.0.1:11239` + `:11240`. Installer builds
set `VITE_API_BASE` (see `native/build.ps1`); dev uses the Vite proxy.

## Biome fails on dist/

`webapp/biome.json` excludes `dist/` + `node_modules` via `files.includes`.
Never commit `dist/` (gitignored).
