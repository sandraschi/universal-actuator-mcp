import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(command="node", args=["D:/Dev/repos/universal-actuator-mcp/dist/index.js"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool(
                "universal_actuator",
                {"domain": "knowledge", "action": "help", "payload": {}},
            )

            # Print the tool result content
            for item in res.content:
                if item.type == "text":
                    try:
                        # Try to format JSON nicely if it is JSON
                        data = json.loads(item.text)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        print(item.text)


asyncio.run(main())
