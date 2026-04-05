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
import { FastMCP } from "fastmcp";
import { z } from "zod";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

/**
 * Universal Actuator MCP 🌐
 *
 * A materialist/reductionist facade that consolidates high-entropy toolsets
 * into a single, unified interface. Supports federating requests to sub-MCP servers
 * with intelligent portmanteau routing.
 */

interface ICognitiveBridge {
    logMilestone(title: string, content: string, tags?: string[]): Promise<void>;
    snapshotProgress(task: string, status: string): Promise<void>;
}

class CognitiveBridge implements ICognitiveBridge {
    async logMilestone(title: string, content: string, tags: string[] = []) {
        console.error(`[CognitiveBridge] Milestone: ${title}`);
        const memServer = Object.keys(FEDERATION_CONFIG).find(name => name.includes("mem") || name.includes("adn"));
        if (memServer) {
            await FLEET.executeTool(memServer, "adn_content", {
                operation: "write",
                title: `Milestone: ${title}`,
                content: content,
                tags: ["#milestone", ...tags].join(",")
            });
        }
    }

    async snapshotProgress(task: string, status: string) {
        console.error(`[CognitiveBridge] Progress: ${task} -> ${status}`);
        const memServer = Object.keys(FEDERATION_CONFIG).find(name => name.includes("mem") || name.includes("adn"));
        if (memServer) {
            await FLEET.executeTool(memServer, "adn_content", {
                operation: "quick",
                content: `Task: ${task}\nStatus: ${status}`,
                tags: "#progress-log"
            });
        }
    }
}

const BRIDGE = new CognitiveBridge();

const server = new FastMCP({
    name: "universal-actuator-mcp",
    version: "1.0.0",
});

interface ServerConfig {
    command: string;
    args: string[];
    env?: Record<string, string>;
    githubUrl?: string; // SOTA: link to install if missing
    mappings?: Record<string, string>; // Maps high-level action to portmanteau tool name
}

interface Config {
    servers?: Record<string, ServerConfig>;
}

/**
 * Metadata for tracking the state of the federation hub.
 */
let FEDERATION_CONFIG: Record<string, ServerConfig> = {};

class FleetAggregator {
    private federatedClients: Record<string, FederationClient> = {};

    async executeTool(domain: string, action: string, payload: any) {
        if (!FEDERATION_CONFIG[domain]) {
            throw new McpError(ErrorCode.InvalidParams, `Domain '${domain}' not found in federation config.`);
        }

        if (!this.federatedClients[domain]) {
            const { isAvailable, reason } = checkAvailability(domain, FEDERATION_CONFIG[domain]);
            if (!isAvailable) {
                throw new McpError(ErrorCode.InternalError, `Domain '${domain}' is not available: ${reason}`);
            }
            this.federatedClients[domain] = new FederationClient(domain, FEDERATION_CONFIG[domain]);
        }

        return this.federatedClients[domain].executeTool(action, payload);
    }

    async closeAll() {
        for (const client of Object.values(this.federatedClients)) {
            await client.close();
        }
        this.federatedClients = {};
    }
}

const FLEET = new FleetAggregator();

/**
 * Universal Tool: universal_milestone
 * Purpose: Synchronize major progress milestones to the Advanced Memory (memops).
 */
server.tool(
    "universal_milestone",
    {
        title: z.string().describe("The title of the milestone"),
        content: z.string().describe("Detailed description of the milestone"),
        tags: z.array(z.string()).optional().describe("Semantic tags (e.g., #milestone, #architecture)"),
    },
    async ({ title, content, tags = [] }) => {
        try {
            await BRIDGE.logMilestone(title, content, tags);
            return {
                content: [{ type: "text", text: `Milestone "${title}" successfully bridged to Advanced Memory.` }],
            };
        } catch (error) {
            return {
                content: [{ type: "text", text: `Failed to bridge milestone: ${error}` }],
                isError: true,
            };
        }
    }
);

function loadConfig() {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);

    // 1. Explicit Local Configs
    const paths = [
        join(process.cwd(), "config.json"),
        join(__dirname, "..", "config.json"),
        join(__dirname, "config.json")
    ];

    for (const configPath of paths) {
        try {
            if (existsSync(configPath)) {
                const config = JSON.parse(readFileSync(configPath, "utf-8")) as Config;
                FEDERATION_CONFIG = { ...FEDERATION_CONFIG, ...(config.servers || {}) };
                console.error(`[Config] Loaded local configuration from ${configPath}`);
            }
        } catch (error) {
            console.error(`[Config] Error reading ${configPath}: ${error}`);
        }
    }

    // 2. "Glom On" Auto-Discovery (SOTA Integration)
    const userProfile = process.env.USERPROFILE || "";
    const appData = process.env.APPDATA || "";

    const discoveryPaths = [
        { name: "Antigravity", path: join(userProfile, ".gemini", "antigravity", "mcp_config.json"), key: "mcpServers" },
        { name: "Claude Desktop", path: join(appData, "Claude", "claude_desktop_config.json"), key: "mcpServers" }
    ];

    for (const discovery of discoveryPaths) {
        try {
            if (existsSync(discovery.path)) {
                console.error(`[Discovery] Glomming onto ${discovery.name} at ${discovery.path}`);
                const content = JSON.parse(readFileSync(discovery.path, "utf-8"));
                const servers = content[discovery.key] || {};

                // Convert common format to our Federation format
                for (const [name, srv] of Object.entries(servers)) {
                    const server = srv as any;
                    if (!FEDERATION_CONFIG[name]) {
                        FEDERATION_CONFIG[name] = {
                            command: server.command,
                            args: server.args || [],
                            env: server.env || {}
                        };
                    }
                }
            }
        } catch (error) {
            console.error(`[Discovery] Failed to glom onto ${discovery.name}: ${error}`);
        }
    }

    console.error(`[Config] Federation table initialized with ${Object.keys(FEDERATION_CONFIG).length} domains.`);
}

function checkAvailability(domain: string, config: ServerConfig): { isAvailable: boolean; reason?: string } {
    try {
        // 1. Check if command is in PATH
        const checkCmd = process.platform === "win32" ? `where ${config.command}` : `which ${config.command}`;
        try {
            execSync(checkCmd, { stdio: "ignore" });
        } catch {
            return { isAvailable: false, reason: `Command '${config.command}' not found in system PATH.` };
        }

        // 2. Check PYTHONPATH/env paths if they point to local repos
        if (config.env?.PYTHONPATH) {
            const paths = config.env.PYTHONPATH.split(process.platform === "win32" ? ";" : ":");
            for (const p of paths) {
                if (!existsSync(p)) {
                    return { isAvailable: false, reason: `Dependency path missing: ${p}` };
                }
            }
        }

        return { isAvailable: true };
    } catch (e) {
        return { isAvailable: false, reason: `Availability check failed: ${e}` };
    }
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

    async executeTool(action: string, payload: any) {
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
                    "A unified interface for performing actions across various domains.\n\n" +
                    "This tool reduces semantic entropy by consolidating specialized domain toolsets (Files, Browser, Robotics, etc.) " +
                    "into a single federation gateway. It intelligently routes requests to the appropriate sub-server " +
                    "based on the specified domain.\n\n" +
                    "Usage Examples:\n" +
                    "- Files: { domain: 'files', action: 'list_directory', payload: { path: 'C:/repos', recursive: true } }\n" +
                    "- Browser: { domain: 'browser', action: 'navigate', payload: { url: 'https://google.com' } }\n" +
                    "- Knowledge: { domain: 'knowledge', action: 'adn_knowledge', payload: { operation: 'search', query: 'mcp' } }",
                inputSchema: {
                    type: "object",
                    properties: {
                        domain: {
                            type: "string",
                            description: "The target domain for the action (e.g., 'files', 'browser', 'robotics', 'knowledge', 'system').",
                        },
                        action: {
                            type: "string",
                            description: "The high-level action to perform within the domain. For portmanteau tools, this is injected as the 'operation' parameter.",
                        },
                        payload: {
                            type: "object",
                            description: "A JSON object containing the parameters required for the specific action. Keys depend on the target domain/action.",
                        },
                    },
                    required: ["domain", "action", "payload"],
                },
            },
            {
                name: "universal_help",
                description:
                    "Get comprehensive documentation and usage examples for federated domains.\n\n" +
                    "Usage:\n" +
                    "- Call without arguments to list all active domains.\n" +
                    "- Pass a 'domain' to get detailed metadata, available actions, and routing heuristics for that specific domain.",
                inputSchema: {
                    type: "object",
                    properties: {
                        domain: {
                            type: "string",
                            description: "The target domain to inspect (e.g., 'files', 'robotics'). If omitted, returns a global federation overview.",
                        },
                    },
                },
            },
            {
                name: "universal_status",
                description:
                    "Check the installation status and health of all federated MCP servers.\n\n" +
                    "This tool identifies which domains are usable and provide GitHub links for installing any missing servers.",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
        ],
    };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    if (name === "universal_status") {
        const domainStatusList = Object.entries(FEDERATION_CONFIG).map(([d, config]) => {
            const { isAvailable, reason } = checkAvailability(d, config);
            const statusEmoji = isAvailable ? "✅" : "⚠️";
            const statusText = isAvailable ? "Installed" : "Missing";
            let line = `- ${statusEmoji} **${d}**: ${statusText}`;
            if (!isAvailable) {
                line += ` (${reason})`;
                if (config.githubUrl) {
                    line += ` - [Install Repository](${config.githubUrl})`;
                }
            }
            return line;
        }).join("\n");

        return {
            content: [{
                type: "text",
                text: `# Universal Actuator: Federation Status 📊\n\nTotal Domains Configured: ${Object.keys(FEDERATION_CONFIG).length}\n\n## Domain Health Registry\n${domainStatusList}\n\n---\n*Materialist/Reductionist Diagnostic Complete.*`
            }]
        };
    }

    if (name === "universal_help") {
        const { domain } = (args || {}) as any;
        if (!domain) {
            const domainList = Object.entries(FEDERATION_CONFIG).map(([d, config]) => {
                const { isAvailable } = checkAvailability(d, config);
                const statusEmoji = isAvailable ? "✅" : "⚠️";
                return `- ${statusEmoji} **${d}** ${!isAvailable && config.githubUrl ? `(Install: ${config.githubUrl})` : ""}`;
            }).join("\n");

            return {
                content: [{
                    type: "text",
                    text: `# Universal Actuator Help 🌐\n\nConsolidating high-entropy domains into a single SOTA interface.\n\n## Configured Domains\n${domainList}\n\n## Usage\nUse \`universal_help(domain: "domain_name")\` for domain-specific documentation.`
                }]
            };
        }

        const config = FEDERATION_CONFIG[domain];
        if (!config) {
            throw new McpError(ErrorCode.InvalidParams, `Domain '${domain}' not found.`);
        }

        const availability = checkAvailability(domain, config);

        return {
            content: [{
                type: "text",
                text: `# Domain: ${domain.toUpperCase()}\n\n- **Status**: ${availability.isAvailable ? "✅ Installed" : `⚠️ Missing (${availability.reason})`}\n${!availability.isAvailable && config.githubUrl ? `- **Install**: ${config.githubUrl}\n` : ""}- **Command**: \`${config.command}\`\n- **Target**: \`${config.args.join(" ")}\`\n${config.mappings ? `\n### Explicit Mappings\n${Object.entries(config.mappings).map(([k, v]) => `- \`${k}\` -> \`${v}\``).join("\n")}` : ""}\n\n### Portmanteau Support\nThis domain supports heuristic fallback to \`_ops\`, \`_system\`, \`_behavior\`, \`_tools\`, and \`_control\` patterns.`
            }]
        };
    }

    if (name !== "universal_actuator") {
        throw new McpError(ErrorCode.MethodNotFound, "Unknown tool");
    }

    const { domain, action, payload } = (args || {}) as any;

    const config = FEDERATION_CONFIG[domain];
    if (!config) {
        throw new McpError(ErrorCode.InvalidParams, `Domain '${domain}' not found.`);
    }

    const availability = checkAvailability(domain, config);
    if (!availability.isAvailable) {
        return {
            content: [{
                type: "text",
                text: `❌ Error: Domain '${domain}' is not available.\nReason: ${availability.reason}${config.githubUrl ? `\n\nPlease install it from: ${config.githubUrl}` : ""}`
            }],
            isError: true
        };
    }

    try {
        // 1. Internal Baseline Handlers
        if (domain === "system") {
            if (action === "info") {
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
            if (action === "help") {
                return {
                    content: [{
                        type: "text",
                        text: `# Universal Actuator System Domain\n\nSupported Actions:\n- **info**: Reporting operational status and federation statistics.\n- **help**: Displays this message.`
                    }]
                };
            }
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

        return await client.executeTool(action, payload);

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
