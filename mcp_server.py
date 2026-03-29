from fastmcp import FastMCP
import httpx
import asyncio

mcp = FastMCP(name="RPI MCP", version="1.0.0")

BASE = "http://localhost:8005"
client = httpx.AsyncClient(base_url=BASE, timeout=15.0)


# --- Helpers ---

async def _equity(endpoint: str, company_id: int):
    resp = await client.get(f"/market/equity/{endpoint}/{company_id}")
    resp.raise_for_status()
    return resp.json()


async def _bulk_equity(endpoints: dict[str, str], company_id: int) -> list[dict]:
    async def fetch(section: str, endpoint: str):
        try:
            data = await _equity(endpoint, company_id)
            return {"section": section, "data": data}
        except Exception as e:
            return {"section": section, "error": str(e)}

    return await asyncio.gather(*(fetch(s, e) for s, e in endpoints.items()))


async def _market(path: str):
    resp = await client.get(f"/market/{path}")
    resp.raise_for_status()
    return resp.json()


# --- Bundle definitions ---

FUNDAMENTALS = {
    "profit_and_loss_ratios": "pnl_ratio",
    "quarterly_results": "quaterly_result",
    "yearly_results": "yearly_result",
    "balance_sheet": "balance_sheet",
    "cash_flow": "cash_flow",
    "financial_ratios": "financial_ratio",
}

VALUATION = {
    "company_details": "company_details",
    "valuation_ratios": "valuation_ratio",
    "growth_ratios": "growth_ratio",
    "dividend_history": "dividend",
    "last_price": "last_price",
}

OWNERSHIP = {
    "major_shareholders": "shareholders",
    "fund_houses_invested": "fund_house",
    "related_companies": "related_companies",
}

NEWS_RESEARCH = {
    "latest_news": "latest_news",
    "corporate_actions": "corporate_news",
    "research_links": "report",
}


# --- Market-wide tools ---

@mcp.tool()
async def market_mood():
    """Get the market mood index"""
    return await _market("mmi")


@mcp.tool()
async def get_investable_bonds() -> list:
    """Get investable secondary market bonds"""
    return await _market("bonds")


@mcp.tool()
async def get_us_index():
    """Get market mood for US market"""
    return await _market("us-index")


@mcp.tool()
async def get_metals_data():
    """Get price of metals"""
    return await _market("metals")


@mcp.tool()
async def get_ipo_data():
    """Get IPO data of Indian market"""
    return await _market("ipo")


# --- Bundled company tools ---

@mcp.tool()
async def get_fundamentals(company_id: int) -> list[dict]:
    """Get full fundamental analysis data for a company.
    Includes: P&L ratios (OPM, NPM, ROE, ROCE), 12 quarters of results,
    10 years of annual results, balance sheet, cash flow statement,
    and financial ratios (ROCE, debt-to-equity, interest coverage).
    Use this when analyzing a company's financial health or performance."""
    return await _bulk_equity(FUNDAMENTALS, company_id)


@mcp.tool()
async def get_valuation(company_id: int) -> list[dict]:
    """Get valuation and pricing data for a company.
    Includes: company overview (market cap, sector, PE, book value),
    valuation ratios (PE, PB, EV/EBITDA), growth ratios (sales/profit/EPS CAGR),
    dividend history, and last closing price.
    Use this when evaluating if a stock is cheap or expensive."""
    return await _bulk_equity(VALUATION, company_id)


@mcp.tool()
async def get_ownership(company_id: int) -> list[dict]:
    """Get ownership and shareholding data for a company.
    Includes: 10-year shareholding pattern (promoter, FII, DII, public %),
    mutual fund houses holding the stock, and related group companies.
    Use this when checking who owns the stock or promoter commitment."""
    return await _bulk_equity(OWNERSHIP, company_id)


@mcp.tool()
async def get_news_and_research(company_id: int) -> list[dict]:
    """Get news and research material for a company.
    Includes: latest news (last 1 year), corporate action news
    (splits, bonuses, buybacks), and research report/presentation links.
    Use this for recent developments or to find analyst reports."""
    return await _bulk_equity(NEWS_RESEARCH, company_id)


@mcp.tool()
async def get_full_company_snapshot(company_id: int) -> list[dict]:
    """Get EVERYTHING about a company in one call.
    Combines fundamentals + valuation + ownership + news/research + about.
    Use this when doing a comprehensive stock analysis or when the user
    asks for a complete picture of a company."""
    all_endpoints = {
        **FUNDAMENTALS, **VALUATION, **OWNERSHIP, **NEWS_RESEARCH,
        "about": "about",
    }
    return await _bulk_equity(all_endpoints, company_id)


# --- Individual tools kept ---

@mcp.tool()
async def get_last_closing_price(company_id: int):
    """Get last closing price of a stock — quick price check"""
    return await _equity("last_price", company_id)


@mcp.tool()
async def get_about_company(company_id: int):
    """Get company description — business overview, founding, key products/services"""
    return await _equity("about", company_id)


@mcp.tool()
async def get_company_research_links(company_id: int):
    """Get PDF/presentation links for company research — broker reports, investor presentations"""
    return await _equity("report", company_id)


@mcp.tool()
async def get_dividend_history(company_id: int):
    """Get dividend history — dates, amounts, yield, payout ratio"""
    return await _equity("dividend", company_id)


async def main():
    await mcp.run_http_async(
        transport="streamable-http", host="0.0.0.0", port=8006, path="/market-mcp/mcp/"
    )

asyncio.run(main())