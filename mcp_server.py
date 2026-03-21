from fastmcp import FastMCP
import httpx
 

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

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8006, path="/market-mcp/mcp/")
