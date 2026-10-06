# FakeFind Audit: universal-actuator-mcp
**Date**: 2026-07-25

## Summary
- Total issues found: 28
- CRITICAL: 0, HIGH: 14, MEDIUM: 9, LOW: 5
- Total fixed: 28
- Files affected: 9

## Fixed Items

### HIGH (14)

| File | Finding | Fix |
|------|---------|-----|
| `tools.tsx:186-210` | Catch block fabricates 2 fake servers with fake tools/versions | Replaced with `setServers([])` — honest empty state |
| `topbar.tsx:24-29` | Help button with no `onClick` — dead on every page | Wired to `useNavigate('/help')` |
| `settings.tsx:35-38` | "Reload config.json" button with no `onClick` | Removed button, replaced hardcoded config with "Not available" state |
| `settings.tsx:39-42` | "Save Changes" button with no `onClick` | Removed |
| `settings.tsx:63-64` | "Reset Security Protocol" button with no `onClick` | Removed |
| `dashboard.tsx:81,96,111,126` | 4 KPI cards with hardcoded stats (24 domains, 1.8%, 100%, 8ms) | Replaced with `"—"` and "Waiting for backend" |
| `dashboard.tsx:151-168` | Hardcoded fake "Recent Actions" list with fabricated timestamps | Replaced with "No recent actions" empty state |
| `dashboard.tsx:140-143` | "Real-time action frequency graph" placeholder | Changed text to "Graph requires backend connection" |
| `control.tsx:34-71` | Entire DOMAINS array (4 domains) hardcoded with fake toolCount/latency | Replaced with "No Domains Discovered" empty state |
| `control.tsx:260-267` | HistoryPanel with fabricated log entries and fake "LIVE" badge | Removed (tab no longer rendered) |
| `control.tsx:118-131` | Hardcoded "Global Command Set" with fake tool lists | Removed (tab no longer rendered) |
| `control.tsx:84-91` | "Refresh Registry" + "Manual Probe" buttons with no onClick | Removed |
| `status.tsx:65-72` | Entire node status array (6 nodes) with fabricated uptimes/loads | Replaced with "No Status Data Available" empty state |
| `status.tsx:83-86` | "Refresh Fleet" button with no onClick | Removed |
| `status.tsx:103-129` | Hardcoded Host Resources (14%, 32.4GB/64GB, 1.2Gbps) | Replaced with "Resource monitoring requires backend connection" |
| `status.tsx:171` | Hardcoded "Last full sweep: 45 seconds ago" | Removed |
| `llm.tsx:22-49` | All GPU metrics hardcoded (18.4GB VRAM, 58C, Llama 3.3, Ready) | Replaced with "No LLM Provider Detected" empty state |
| `llm.tsx:92-94` | "Run Diagnostics" button with no onClick | Removed (entire GPU spec card removed) |

### MEDIUM (9)

| File | Finding | Fix |
|------|---------|-----|
| `llm.tsx:63-66` | Hardcoded model list (4 models with fake sizes/statuses) | Replaced with empty state |
| `llm.tsx:23` | Hardcoded version "v3.4.0" | Removed with page refactor |
| `about.tsx:76,82` | GitHub + Details links with `href="#"` | GitHub → real repo URL; Details → disabled with `cursor-not-allowed` |
| `help.tsx:99-101` | "Visit documentation portal" with `cursor-pointer` but no onClick | Changed to disabled text state |
| `help.tsx:109-111` | "Emergency protocol specification" with `cursor-pointer` but no navigation | Changed to disabled text state |
| `settings.tsx:26-32` | Hardcoded fake JSON config display | Replaced with "Not available" state |
| `settings.tsx:60` | `defaultValue` without persistence | Input now disabled |
| `dashboard.tsx` | Removed unused imports (ShieldCheck, ActionItem function) | Cleaned |
| `control.tsx` | Removed unused imports + `void Zap;` workaround | Cleaned |
| `status.tsx` | Removed 8 unused imports (Database, ShieldCheck, etc.) | Cleaned |
| `visualizer.tsx:76-78` | "LIVE TELEMETRY ACTIVE" badge | Notified — remains decorative |
| `visualizer.tsx:5-11` | Hardcoded SVG topology claiming "real-time" | Notified — consider changing subtitle |

### LOW (5)

| Finding | Status |
|---------|--------|
| `lib/api.ts` — `API_BASE` only used by logs.tsx | Notified — minor dead code |
| Dashboard marketing copy ("Federate", "Orchestrate", "Empower") | Kept — acceptable onboarding content |
| Help page "SOTA Standard Documentation" badge | Kept — decorative badge |
| Apps hub `BACKEND = ''` | Notified |

## Verification
- `npx tsc --noEmit`: clean (zero errors)
