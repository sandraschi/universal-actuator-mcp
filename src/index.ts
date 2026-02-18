#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    CallToolResultSchema,
    ErrorCode,
    ListToolsRequestSchema,
    ListToolsResultSchema,
    McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

/**
 * Universal Actuator MCP 🌐
 * 
 * A materialist/reductionist facade that consolidates high-entropy toolsets
 * into a single, unified interface. Supports federating requests to sub-MCP servers
 * with intelligent portmanteau routing.
 */

const server = new Server(
    {
        name: "universal-actuator-mcp",
        version: "1.0.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

interface ServerConfig {
    command: string;
    args: string[];
    env?: Record<string, string>;
    mappings?: Record<string, string>; // Maps high-level action to portmanteau tool name
}

interface Config {
    servers?: Record<string, ServerConfig>;
}

let FEDERATION_CONFIG: Record<string, ServerConfig> = {};

function loadConfig() {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);

    const paths = [
        join(process.cwd(), "config.json"),
        join(__dirname, "..", "config.json"),
        join(__dirname, "config.json")
    ];

    for (const configPath of paths) {
        try {
            if (existsSync(configPath)) {
                const config = JSON.parse(readFileSync(configPath, "utf-8")) as Config;
                FEDERATION_CONFIG = config.servers || {};
                console.error(`[Config] Loaded configuration from ${configPath}`);
                return;
            }
        } catch (error) {
            console.error(`[Config] Error reading ${configPath}: ${error}`);
        }
    }
    console.error("[Config] No config.json found. Running with empty federation table.");
}

class FederationClient {
    private client: Client | null = null;
    private transport: StdioClientTransport | null = null;

    constructor(private domain: string, private config: ServerConfig) { }

    async connect() {
        if (this.client) return this.client;

        console.error(`[Federation] Spawning sub-server for domain: ${this.domain}`);
        this.transport = new StdioClientTransport({
            command: this.config.command,
            args: this.config.args,
            env: {
                ...process.env as Record<string, string>,
                ...this.config.env as Record<string, string>,
            },
        });

        this.client = new Client(
            {
                name: `ua-client-${this.domain}`,
                version: "1.0.0",
            },
            {
                capabilities: {},
            }
        );

        await this.client.connect(this.transport);
        return this.client;
    }

    async callTool(action: string, payload: any) {
        const client = await this.connect();

        // 1. Resolve Tool Mapping (support portmanteau servers)
        let toolName = action;
        let toolArgs = { ...payload };

        // Check for project-specific mapping
        if (this.config.mappings && this.config.mappings[action]) {
            toolName = this.config.mappings[action];
            // If mapping exists, the original action becomes the 'operation' field for SOTA portmanteaus
            toolArgs = { operation: action, ...payload };
        }

        // 2. Discover if tool exists
        const toolList = await client.request(
            { method: "tools/list" },
            ListToolsResultSchema
        );

        let targetTool = toolList.tools.find(t => t.name === toolName);

        // 3. Heuristic discovery: if toolName doesn't exist, search for common portmanteau pattern suffix
        if (!targetTool) {
            const pattern = ["_ops", "_system", "_control", "_behavior", "_tools"];
            for (const p of pattern) {
                const portmanteau = toolList.tools.find(t => t.name.endsWith(p));
                if (portmanteau) {
                    console.error(`[Federation] Action '${toolName}' not found. Falling back to portmanteau '${portmanteau.name}'`);
                    toolName = portmanteau.name;
                    toolArgs = { operation: action, ...payload };
                    targetTool = portmanteau;
                    break;
                }
            }
        }

        if (!targetTool) {
            throw new McpError(
                ErrorCode.InvalidParams,
                `Action '${action}' (resolved as '${toolName}') not found in sub-server for domain '${this.domain}'`
            );
        }

        console.error(`[Federation] Routing '${action}' -> tool '${toolName}' with payload keys: ${Object.keys(toolArgs)}`);

        return await client.request(
            {
                method: "tools/call",
                params: {
                    name: toolName,
                    arguments: toolArgs,
                },
            },
            CallToolResultSchema
        );
    }

    async close() {
        if (this.transport) {
            await this.transport.close();
            this.client = null;
            this.transport = null;
        }
    }
}

const federatedClients: Record<string, FederationClient> = {};

server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "universal_actuator",
                description:
                    "A unified interface for performing actions across various domains. " +
                    "Reduces semantic entropy by consolidating domain-specific tools into a single entry point.",
                inputSchema: {
                    type: "object",
                    properties: {
                        domain: {
                            type: "string",
                            description: "The target domain (e.g., 'files', 'browser', 'system', 'blender', 'gimp').",
                        },
                        action: {
                            type: "string",
                            description: "The action to perform (e.g., 'read_file', 'snapshot', 'render').",
                        },
                        payload: {
                            type: "object",
                            description: "Parameters for the action.",
                        },
                    },
                    required: ["domain", "action", "payload"],
                },
            },
        ],
    };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== "universal_actuator") {
        throw new McpError(ErrorCode.MethodNotFound, "Unknown tool");
    }

    const { domain, action, payload } = request.params.arguments as any;

    try {
        // 1. Internal Baseline Handlers
        if (domain === "system" && action === "info") {
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify({
                        status: "operational",
                        philosophy: "Materialist/Reductionist",
                        federation_count: Object.keys(FEDERATION_CONFIG).length,
                        active_domains: Object.keys(FEDERATION_CONFIG)
                    }, null, 2)
                }]
            };
        }

        // 2. Route to Federated Sub-Server
        const config = FEDERATION_CONFIG[domain];
        if (!config) {
            throw new McpError(
                ErrorCode.InvalidParams,
                `Domain '${domain}' is not configured. Configured: ${Object.keys(FEDERATION_CONFIG).join(", ")}`
            );
        }

        let client = federatedClients[domain];
        if (!client) {
            client = new FederationClient(domain, config);
            federatedClients[domain] = client;
        }

        return await client.callTool(action, payload);

    } catch (error) {
        console.error(`[Universal Actuator] Error in domain '${domain}': ${error}`);
        return {
            content: [
                {
                    type: "text",
                    text: `Execution failure: ${error instanceof Error ? error.message : String(error)}`,
                },
            ],
            isError: true,
        };
    }
});

process.on("SIGINT", async () => {
    for (const domain in federatedClients) {
        await federatedClients[domain].close();
    }
    process.exit(0);
});

loadConfig();
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("[Universal Actuator] Facade operational.");
