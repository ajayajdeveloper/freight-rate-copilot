import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(SCRIPT_DIR, "../../mcp-server/server.mjs")


async def main():
    client = MultiServerMCPClient({
        "freight": {
            "command": "node",
            "args": [SERVER_PATH],
            "transport": "stdio",
        }
    })

    tools = await client.get_tools()
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"  Description: {tool.description}")
        print(f"  Args: {tool.args}")

    get_rate = tools[0]
    result = await get_rate.ainvoke({
        "carrier_code": "XPOL",
        "origin": "Los Angeles, CA",
        "destination": "Dallas, TX",
        "weight_lbs": 300,
    })
    print("\nResult:", result)


asyncio.run(main())
