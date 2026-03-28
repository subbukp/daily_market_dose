from fastmcp.client.transports.stdio import NodeStdioTransport, PythonStdioTransport
from fastmcp.client.transports.sse import SSETransport
from fastmcp.client.transports.http import StreamableHttpTransport

import asyncio
import json
from fastmcp import Client, FastMCP

server = FastMCP("TestServer")

client = Client[PythonStdioTransport | NodeStdioTransport | SSETransport | StreamableHttpTransport]("https://misapprehensively-fleshliest-michelina.ngrok-free.dev/market-mcp/mcp")
#client = Client("https://mcp.swiggy.com/im")
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