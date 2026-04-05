import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def check_tools():
    # Configure the server command
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "filesystem_mcp", "--stdio"],
        env={
            **os.environ,
            "PYTHONPATH": "D:/Dev/repos/filesystem-mcp/src",
            "PYTHONUNBUFFERED": "1",
        },
    )

    print("Connecting to filesystem-mcp...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print("\nExposed Tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description[:50]}...")


if __name__ == "__main__":
    asyncio.run(check_tools())
