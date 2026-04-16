# Changelog — Universal Actuator MCP Hub

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] — 2026-04-11

### Added
- Standardized `universal_actuator` portmanteau tool per SOTA v14.1.
- Standardized `universal_status` health monitoring.
- Root `/` REST endpoint for availability verification.
- `/telemetry` REST endpoint for real-time fleet analytics.

### Changed
- Migrated to **FastMCP 3.2.3** (SOTA reductionist standard).
- Hardened REST routes to resolve 404 synchronization errors.
- Refactored `FleetManager` for reductionist alignment.
- Updated `justfile` with operational industrial recipes.

## [2.0.0] — 2026-03-30

### 🧠 Modern AI & Vector RAG (March 2026 SOTA)

#### Backend (Advanced AI Integration)
- **LanceDB Vector RAG**: Implemented a local vector database using LanceDB for semantic search across federated media metadata (Calibre, Plex, Immich).
- **[SEP-1577] Agentic Workflow**: Added `agentic_workflow_tool` leveraging `ctx.sample()` for autonomous "Plan → Execute → Audit" mission orchestration.
- **RAG Ingestion**: Developed `ingest_fleet_to_rag` tool for bulk-embedding metadata using `sentence-transformers` (all-MiniLM-L6-v2) with deterministic hash fallbacks.
- **Proactive Diagnostics**: Enhanced `glom_on` discovery with wide-range port scanning (10700-10900) and configuration file analysis.

#### Frontend (Real-time Federation)
- **Tele-Status 2.0**: Upgraded the `/status` page to prioritize real-time health telemetry across the 15-node grid, featuring dynamic glassmorphism indicators and Lucide icon sets.
- **Library RAG Integration**: Wired the `/library` search to favor the semantic RAG index when the "Semantic" toggle is active.

#### DevOps
- **SOTA 3.1 Compliance**: Verified 100% adherence to **FastMCP 3.1** standards and **WEBAPP_PORTS.md** registry.
- **Version Normalization**: Aligned the core backend as `v2.0.0` to reflect architectural maturity.

---

## [1.3.0] — 2026-03-29

### 🚀 Fleet Expansion & SOTA 2026 Refactor

#### Backend (FastMCP 3.1 Migration)
- **Migrated to FastMCP 3.1**: Updated core server logic to align with the March 2026 SOTA standard.
- **Routing Modernization**: Refactored the internal ASGI application from `mcp.app` to **`mcp.http_app`** to resolve attribute regressions and ensure stable REST communication.
- **Startup Automation**: Synchronized `start.ps1` to target the new `.http_app` attribute, resolving the `AttributeError` during fleet boot.

#### Frontend (Vite + React 19 Conversion)
- **Framework Realignment**: Successfully transitioned the dashboard from Next.js to **Vite + React 19** for superior build speed and SOTA compliance.
- **Status Dashboard**: Added a high-fidelity **System Status** page (`/status`) with real-time health telemetry across the 15-node federation, featuring glassmorphism cards and Lucide icons.
- **UI Repair**: Fixed a critical JSX corruption in the **Media Library** (`/library`), restoring the federated search and filter header.
- **Navigation Sync**: Refactored the **Sidebar** and **App Router** to include the new Status page and corrected default imports for standard components.

#### DevOps & Docs
- **README Deep-Refresh**: Synchronized the root documentation with the actual framework stack (Vite/React) and updated architecture diagrams.
- **SOTA Audit**: Verified 100% compliance with **WEBAPP_PORTS.md** (reserved range 10700-10800+).

---

## [1.1.0] — 2026-03-02

### 🌐 Frontend — New Pages & Live Data

#### Added
- **`/library` page** (`frontend/src/app/library/page.tsx`): Federated media browser wired to `GET /library`. Supports full-text search + domain filter tabs (`All / Media / Books / Photos`). Responsive card grid with source badges.
- **`/chat` page** (`frontend/src/app/chat/page.tsx`): Command dispatch terminal with live response stream from `POST /chat`.
- **Library** and **Chat** navigation links added to the sidebar (`Sidebar.tsx`).

#### Changed
- **Dashboard** (`/`): Upgraded from static mock data to live data:
  - Polls `GET /telemetry` every 5 seconds for real CPU/memory/uptime.
  - Fetches `GET /milestones` on mount and displays last 5 milestones as a timeline.
  - Online/Connecting status indicator with formatted uptime display.
- **Fleet page** (`/fleet`): Fixed data shape mismatch — backend returns `discovered_servers[].name`, frontend was reading `servers[].id`. Corrected mapping to use `discovered_servers` array and `name`, `url`, `active` fields.

#### Fixed
- Progress bar components: removed incorrect CSS-variable inline-style pattern; replaced with direct `style={{ width: '...' }}` (standard React dynamic-width pattern).
- Removed stale `eslint-disable-next-line react/forbid-component-props` comments that were wrongly referencing the rule name.

---

### 🔧 Backend — New REST Endpoints

#### Added
- **`GET /milestones`** (`@mcp.app.get("/milestones")`): REST HTTP endpoint exposing milestone history so the dashboard can poll it. Previously `get_milestones_history` was only available as an MCP tool.

---

## [1.0.0] — 2026-02-28

### 🚀 Initial Release

#### Backend (`backend/server.py`)
- FastMCP 2.14.5 server with SSE transport on port **10857**.
- MCP Tools:
  - `search_federated(query, domain)` — fan-out search to Calibre + Plex subservers.
  - `glom_on()` — auto-discover all active MCP servers in port range 10700–10900.
  - `universal_milestone(title, description, type)` — persistent milestone logging to `backend/state/milestones.json`.
  - `get_milestones_history()` — retrieve full milestone log.
  - `get_fleet_telemetry()` — real-time psutil metrics + node count.
  - `federated_search(query)` — cross-node structured search.
- REST Endpoints:
  - `GET /glom_on` — fleet discovery.
  - `GET /telemetry` — CPU, memory, uptime, milestone count.
  - `GET /library` — federated media search (Calibre + Plex fan-out, demo fallback).
  - `POST /chat` — command dispatch with fleet search.
  - `POST /launch` — detached-process launch via registered `start.ps1` scripts.
- App launch registry (`APP_LAUNCH_REGISTRY`) cross-referenced with `apps-catalog.ts`.

#### Frontend (`frontend/`)
- Next.js 16 + Tailwind CSS dashboard on port **10720**.
- Pages: `/` (Dashboard), `/fleet`, `/tools`.
- Glassmorphism design system with `glass-card`, `btn-primary`, CSS custom properties.
- Sidebar navigation with real-time status indicator.
- Dynamic font (Geist) via `next/font`.

#### DevOps
- `frontend/start.ps1` + `frontend/start.bat` for one-click launch.
- Next.js 16.1.6 (Turbopack) — clean production build verified.
- `glama.json` manifest for Glama.ai marketplace registration.
- `.pre-commit-config.yaml` for Ruff linting gate.

---

**Legend:**
- **Added** — new features
- **Changed** — changes to existing functionality
- **Fixed** — bug fixes
- **Removed** — removed features
- **Security** — security patches
