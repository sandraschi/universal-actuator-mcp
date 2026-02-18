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

-   **domain**: The target domain (`browser`, `office`, `system`)
-   **action**: The specific action to perform
    -   *Browser*: `navigate`, `click`, `type`, `screenshot`
    -   *Office*: `open`, `read`, `write`
    -   *System*: `exec`, `info`
-   **payload**: JSON parameters for the action

## 🤖 AI & Hardware Requirements

This server itself is a lightweight router and does **not** use local AI models. However, the **sub-servers** you configure may have their own requirements.

-   **Universal Actuator**: Minimal resources (Node.js runtime)
-   **Sub-Servers**: Check individual documentation.
    -   *Example*: If routing to a local vision model server, a GPU (RTX 3060+) may be required.

## 📜 License

MIT
