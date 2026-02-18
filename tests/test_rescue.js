import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import {
    CallToolResultSchema,
    ListToolsResultSchema
} from "@modelcontextprotocol/sdk/types.js";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { existsSync } from "fs";

/**
 * Universal Actuator Rescue Verification Script v2.1 🚀
 * 
 * Verifies the Actuator's ability to handle internal system domains
 * and federate to sub-servers with portmanteau routing.
 */

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testRescue() {
    console.log("🚀 Starting Universal Actuator Rescue Verification...");

    const serverPath = join(__dirname, "..", "dist", "index.js");
    if (!existsSync(serverPath)) {
        console.error("❌ dist/index.js not found. Did you run npm run build?");
        process.exit(1);
    }

    const transport = new StdioClientTransport({
        command: "node",
        args: [serverPath],
    });

    const client = new Client(
        { name: "test-rescue-client", version: "1.0.0" },
        { capabilities: {} }
    );

    try {
        await client.connect(transport);
        console.log("✅ Connected to Universal Actuator");

        // 0. Test Tool Discovery
        console.log("\n--- Testing Tool Discovery ---");
        try {
            const tools = await client.request(
                { method: "tools/list" },
                ListToolsResultSchema
            );
            console.log("Available Tools:", tools.tools.map(t => t.name).join(", "));
        } catch (e) {
            console.error("❌ Tool Discovery Failed:", e);
        }

        // 1. Test Internal System Domain
        console.log("\n--- Testing Internal System Domain ---");
        try {
            const infoResult = await client.request(
                {
                    method: "tools/call",
                    params: {
                        name: "universal_actuator",
                        arguments: {
                            domain: "system",
                            action: "info",
                            payload: {}
                        },
                    },
                },
                CallToolResultSchema
            );
            console.log("Info Result Content:", JSON.stringify(infoResult.content, null, 2));
        } catch (e) {
            console.error("❌ Internal Domain Failed:", e);
            if (e.stack) console.error(e.stack);
        }

        // 2. Test Federated File Domain
        console.log("\n--- Testing Federated Files Domain ---");
        try {
            const fileResult = await client.request(
                {
                    method: "tools/call",
                    params: {
                        name: "universal_actuator",
                        arguments: {
                            domain: "files",
                            action: "file_exists",
                            payload: { path: "package.json" }
                        },
                    },
                },
                CallToolResultSchema
            );
            console.log("File Result Content:", JSON.stringify(fileResult.content, null, 2));
        } catch (e) {
            console.error("❌ Federated Domain Failed:", e);
        }

        // 3. Test Federated Knowledge Domain
        console.log("\n--- Testing Federated Knowledge Domain ---");
        try {
            const knowledgeResult = await client.request(
                {
                    method: "tools/call",
                    params: {
                        name: "universal_actuator",
                        arguments: {
                            domain: "knowledge",
                            action: "status",
                            payload: {}
                        },
                    },
                },
                CallToolResultSchema
            );
            console.log("Knowledge Result Content:", JSON.stringify(knowledgeResult.content, null, 2));
        } catch (e) {
            console.error("❌ Knowledge Domain Test Failed (Expected if server not running):", e.message);
        }

        // 4. Test Federated Robotics Domain
        console.log("\n--- Testing Federated Robotics Domain ---");
        try {
            const roboticsResult = await client.request(
                {
                    method: "tools/call",
                    params: {
                        name: "universal_actuator",
                        arguments: {
                            domain: "robotics",
                            action: "status",
                            payload: {}
                        },
                    },
                },
                CallToolResultSchema
            );
            console.log("Robotics Result Content:", JSON.stringify(roboticsResult.content, null, 2));
        } catch (e) {
            console.error("❌ Robotics Domain Test Failed (Expected if server not running):", e.message);
        }

        console.log("\n✨ Verification Complete!");
    } catch (error) {
        console.error("\n❌ Global Verification Failed:", error);
        if (error.stack) console.error(error.stack);
    } finally {
        try {
            await transport.close();
        } catch (e) { }
    }
}

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

testRescue();
