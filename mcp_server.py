from fastmcp import FastMCP
import httpx
import asyncio
 

mcp = FastMCP(name="RPI MCP", version="1.0.0")

@mcp.tool
def market_mood():
    """
    Get the market mood index
    """
    return httpx.get("http://localhost:8005/market/mmi").json()

@mcp.tool()
def get_investable_bonds() -> list:
    """Get investable secondary bonds"""
    return httpx.get("http://localhost:8005/market/bonds").json()

async def main():
    await mcp.run_http_async(transport="streamable-http", host="0.0.0.0", port=8006, path="/market-mcp/mcp/")

asyncio.run(main())