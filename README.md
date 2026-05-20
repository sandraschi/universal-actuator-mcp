# Universal Actuator MCP Hub (Federation Gateway)

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

> **Federated consumption router and live-dashboard hub for the RoboFang fleet (Plex, Calibre, Immich).**

[![FastMCP](https://img.shields.io/badge/FastMCP-3.1.1-blue)](https://github.com/jlowin/fastmcp)
[![Vite](https://img.shields.io/badge/Vite-6-purple)](https://vitejs.dev/)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev/)
[![Port](https://img.shields.io/badge/Backend-10745-orange)](http://localhost:10745)
[![Port](https://img.shields.io/badge/Frontend-10744-green)](http://localhost:10744)
[![Status](https://img.shields.io/badge/Status-v2.0.0-emerald)]()

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/universal-actuator-mcp
cd universal-actuator-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:

## Overview

The Universal Actuator Hub is a **Federation Gateway** refactored to serve as the discovery and routing layer for the wider **RoboFang** fleet. It acts as the "Command & Control" center for the 15+ node ecosystem.

- **Federated Search**: Aggregating results from Plex, Calibre, and Immich concurrently.
- **Fleet Discovery**: Real-time monitoring of all nodes in the 10700-10800+ port range.
- **Milestone Tracking**: Unified logging of agentic accomplishments.
- **SOTA UI/UX**: Premium dashboard built with React 19, Tailwind CSS, and Radix UI.

### Actuator Domains (15+ Nodes)

| Domain | Integrated Services |
|--------|---------------------|
| **Infrastructure** | Filesystem, Windows Operations (WinOps), Virtualization (VirtOps), Browser (Playwright) |
| **Knowledge** | Advanced Memory (adn), DocsOps (Central Docs), FastSearch |
| **Media** | Plex, Calibre, Immich |
| **Creative** | Blender, GIMP, Inkscape |
| **Robotics** | Robotics-MCP, OSC, Unity3D, VRChat, Avatar |

| Layer | Stack | Port | Purpose |
|-------|-------|------|---------|
| **MCP Backend** | FastMCP 3.2.0 + Python | `10745` (`sse`) | MCP tools + REST API Gateway |
| **Web Dashboard** | Vite + React 19 + Tailwind | `10744` | Live fleet monitoring & control |

The backend exposes both **MCP tools** (for IDE agents) and **REST HTTP endpoints** (for the frontend dashboard) via a single FastMCP `mcp.http_app` ASGI application.

---

## Architecture

```

                       Universal Actuator Federation Gateway              
               (FastMCP 3.2.0 | src/universal_actuator_mcp/server.py)       
                                                                         
  MCP Tools (Agentic)            REST API (Dashboard)                    
                                  
  search_all (federated)         GET  /api/v1/health                     
  glom_on (discovery)            GET  /api/v1/glom_on                    
  universal_milestone            GET  /telemetry                         
  get_fleet_telemetry            GET  /milestones                        
                                                                         
  Actuator Fan-out (15+ Nodes)   Downstream Transports                   
                        
  Infrastructure (WinOps/FS)     stdio (sub-process spawn)               
  Knowledge (Memory/Docs)        stdio (sub-process spawn)               
  Media (Calibre/Plex/Immich)    stdio (sub-process spawn)               
  Robotics (OSC/Unity)           udp/stdio                               

                          SSE / REST (localhost:10745)
              
                  Vite Frontend    
                 localhost:10744    
                                   
                /           Dashboard + live telemetry
                /status     Federation health & node status
                /library    Federated media browser
                /tools      GrokTools catalog
                /settings   Gateway configuration
              
```

---

## MCP Tools

### Federated Search & Discovery
| Tool | Description |
|------|-------------|
| `search_federated(query, domain)` | Parallel fan-out search across Calibre, Plex, Immich, and Memory nodes. |
| `glom_on()` | Auto-discover and register all active MCP servers in port range 1070010900. |
| `get_fleet_telemetry()` | Real-time CPU, memory, active node count, and host uptime. |

### RAG & Semantic Analysis
| Tool | Description |
|------|-------------|
| `rag_semantic_search(query, limit, source)` | High-precision vector search via LanceDB (all-MiniLM-L6-v2). |
| `ingest_fleet_to_rag()` | Bulk-populate the vector index from all discovered media sources. |
| `rag_stats()` / `rag_clear()` | Monitor index health or perform a fresh index rebuild. |

### Milestone & Agentic Workflow
| Tool | Description |
|------|-------------|
| `agentic_workflow_tool(goal)` | [SEP-1577] Autonomous multi-step orchestration via `ctx.sample()`. |
| `universal_milestone(title, description, type)` | Log a persistent milestone to the centralized fleet audit trail. |
| `get_milestones_history()` | Retrieve the full historical record of agentic accomplishments. |

---

## REST Endpoints (Internal Gateway)

All internal endpoints are served via `mcp.http_app` on `http://localhost:10745`:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Gateway health check + RAG stats |
| `GET` | `/api/v1/glom_on` | Returns JSON of all auto-discovered fleet nodes |
| `GET` | `/telemetry` | Real-time host and federation metrics |
| `GET` | `/milestones` | JSON log of all fleet-wide accomplishments |

---

## Startup & Deployment

### Automated Launch
The project includes a robust PowerShell orchestration script that clears port squatters and launches both the backend and frontend.

```powershell
# Run from the project root:
.\start.ps1
```

### Manual Individual Launch
**Backend (FastMCP SSE)**:
```powershell
uv run uvicorn universal_actuator_mcp.server:mcp.http_app --host 127.0.0.1 --port 10745
```

**Frontend (Vite Dev)**:
```powershell
cd webapp; npm run dev
```

### IDE Configuration (Antigravity)
Add this to your `mcp_config.json`:
```json
{
  "mcpServers": {
    "universal-actuator": {
      "command": "uv",
      "args": ["--directory", "D:/Dev/repos/universal-actuator-mcp", "run", "uvicorn", "universal_actuator_mcp.server:mcp.http_app", "--host", "127.0.0.1", "--port", "10745"],
      "cwd": "D:/Dev/repos/universal-actuator-mcp"
    }
  }
}
```

---

## Dashboard Routing

| Page | Route | Data Source |
|------|-------|-------------|
| **Dashboard** | `/` | Aggregated telemetry and milestone feed |
| **Status** | `/status` | Real-time node status and federation health cards |
| **Library** | `/library` | Federated asset search across Calibre, Plex, and Immich |
| **Apps Hub** | `/apps` | Fleet-wide app launcher and discovery grid |
| **GrokTools** | `/tools` | Dynamic MCP tool schema analyzer |
| **Settings** | `/settings` | Config manager for downstream servers |

---

## Development

- **Architecture**: Materialist & Reductionist design. Data constitutes the only reality.
- **Frontend**: React 19 with Lucide icons and Framer Motion transitions.
- **Backend**: FastMCP 3.2.0 with async `stdio` client orchestration and **LanceDB RAG**.
- **Agentic Logic**: SEP-1577 "Plan-Execute-Audit" workflows via `ctx.sample()`.

---

## Technical Debt & Roadmap
- [ ] Implement secure `HTTPS` transport for remote federation access.
- [ ] Add `GPU` telemetry monitoring for RTX 4090 performance tracking.
- [ ] Expand `Glom On` to include auto-discovery of local LLM endpoints (Ollama).

---

See [CHANGELOG.md](./CHANGELOG.md) for version history.

*Built with Agentic Precision for the RoboFang Fleet.*
*Maintainer: [sandraschi](https://github.com/sandraschi)*


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.
