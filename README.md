# Universal Actuator MCP 🌐

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://www.typescriptlang.org/)
[![MCP SDK](https://img.shields.io/badge/MCP_SDK-1.26.0-green)](https://modelcontextprotocol.io)
[![Status](https://img.shields.io/badge/Status-BETA-orange)](README.md)
[![Federation](https://img.shields.io/badge/Pattern-Federation_Facade-purple)](README.md#architecture)

**A materialist/reductionist facade that consolidates high-entropy toolsets into a single, unified interface.**

This server acts as a **Federation Router**, accepting a universal action schema and routing it to appropriate domain-specific sub-servers (like `browser-mcp`, `office-mcp`, etc.).

## 🏗️ Architecture

Instead of exposing 50+ individual tools to an LLM (increasing cognitive load and semantic entropy), this server exposes **ONE** tool: `universal_actuator`.

```typescript
// The Universal Interface
universal_actuator({
  domain: "browser",  // or "office", "system"
  action: "navigate", // or "click", "type", etc.
  payload: { url: "https://example.com" }
})
```

The server then:
1.  Identifies the target `domain`
2.  Spawns/Connects to the configured Sub-MCP Server for that domain
3.  Translates/Forwards the request
4.  Returns the result

## 🚀 Quick Start

### Installation

```bash
npm install
npm run build
```

### Configuration (`config.json`)

Define your sub-servers in `config.json`:

```json
{
  "servers": {
    "browser": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "system": {
      "command": "python",
      "args": ["-m", "windows_operations_mcp"]
    }
  }
}
```

### Usage with Claude/Antigravity

```json
{
  "mcpServers": {
    "universal-actuator": {
      "command": "node",
      "args": ["path/to/universal-actuator-mcp/dist/index.js"]
    }
  }
}
```

## 🛠️ Tools

### `universal_actuator`
Performs an action in a specific domain.

-   **domain**: The target domain (`files`, `browser`, `robotics`, `knowledge`, `system`, etc.)
-   **action**: The specific action to perform (e.g., `read_file`, `status`, `info`)
-   **payload**: JSON parameters for the action. These are forwarded directly to the sub-server.

### `universal_help`
Access internal documentation and usage examples for federated domains.

-   **domain**: (Optional) Specific domain for detailed docs.

### `universal_status`
Check the installation status and health of all federated sub-servers.
Lists usable domains and provides GitHub links for remediation of missing ones.

## 📖 Usage Examples

### 1. File Management (Portmanteau Routing)
The Actuator automatically routes specific actions to the `file_ops` or `dir_ops` tools in the `files` domain.

```json
universal_actuator(
  domain: "files",
  action: "read_file",
  payload: { "path": "package.json" }
)
```

### 2. Robotics Control
Control both virtual and physical robots through the `robotics` domain.

```json
universal_actuator(
  domain: "robotics",
  action: "status",
  payload: {}
)
```

### 3. Knowledge Base Search
Search the Advanced Memory knowledge base.

```json
universal_actuator(
  domain: "knowledge",
  action: "adn_knowledge",
  payload: { "operation": "search", "query": "universal actuator" }
)
```

## 🧠 .mcpb Packaging

This repository follows the Anthropic **Skills** format for `.mcpb` distribution:
- `SKILL.md`: Main manifest and usage guide.
- `prompts/`: Standardized prompt templates for cross-domain orchestration.
- `src/`: Core TypeScript implementation.

## 📜 License

MIT
