import asyncio
import json
from fastmcp import Client, FastMCP

server = FastMCP("TestServer")

client = Client("https://corps-duty-morgan-quantities.trycloudflare.com/mcp")

async def main():
    async with client:
        await client.ping()
        
        tools = await client.list_tools()
        
        result = await client.call_tool("market_mood")
        print(tools)
        
        raw = result.content[0].text
        data = json.loads(raw)
        print(json.dumps(data, indent=2))
    
asyncio.run(main())