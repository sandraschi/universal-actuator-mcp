---
name: universal-actuator
description: A unified interface for performing actions across various domains (Files, Browser, Robotics, etc.). Consolidates specialized toolsets into a single federation gateway.
---

# Universal Actuator 🌐

The Universal Actuator is a SOTA federation gateway designed to consolidate specialized MCP domains into a single, high-fidelity interface. It reduces semantic entropy by providing a unified entry point for system actions, file operations, robotics control, and creative automation.

## When to Use

**Use this skill for:**
- Multi-domain workflows (e.g., browsing a site and then performing file operations)
- Consolidating high-entropy toolsets into a single interface
- Federating specialized servers like Robotics, Meta, and Browser
- Standardizing portmanteau routing via intelligent heuristics

**Don't use for:**
- Simple, single-domain tasks where a specific MCP server is already active
- High-performance data streaming (direct domain access preferred)

## Federated Domains

| Domain | Description | Tool Type |
| :--- | :--- | :--- |
| **system** | Internal status and baseline help | Native |
| **files** | File and directory operations | Portmanteau (`file_ops`, `dir_ops`) |
| **browser** | Playwright-based web automation | Standard |
| **robotics** | Control for physical and virtual robots | Portmanteau (`robotics_system`, `robot_behavior`) |
| **knowledge** | Advanced Memory and KB management | Portmanteau (`adn_knowledge`) |
| **meta** | MCP server development and debugging | Standard |
| **generative** | Blender, GIMP, and Inkscape control | Portmanteau |

## Core Tools

### `universal_actuator`
The primary gateway for performing actions.
- **domain**: Target domain (e.g., `files`)
- **action**: High-level action (e.g., `read_file`)
- **payload**: JSON object containing specific parameters

### `universal_help`
Access internal documentation and usage examples.
- **domain**: Specific domain for detailed docs, or omit for a global overview.

## Usage Examples

### Listing Directories
```json
universal_actuator(
  domain: "files",
  action: "list_directory",
  payload: { path: "D:/Dev/repos", recursive: false }
)
```

### Checking System Info
```json
universal_actuator(
  domain: "system",
  action: "info",
  payload: {}
)
```

### Robotics Status
```json
universal_actuator(
  domain: "robotics",
  action: "status",
  payload: {}
)
```

## Prompt Templates
See the `prompts/` directory for mission-critical templates:
- `domain_action.md`: Standard template for cross-domain orchestration.
- `file_search_flow.md`: Optimized flow for finding and analyzing codebase content.

---

**SOTA Federation Gateway v1.0.0**
Materialist/Reductionist Architecture
