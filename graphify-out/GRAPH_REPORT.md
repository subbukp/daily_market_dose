# Graph Report - .  (2026-05-09)

## Corpus Check
- Corpus is ~15,733 words - fits in a single context window. You may not need a graph.

## Summary
- 369 nodes · 460 edges · 41 communities (23 shown, 18 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.84)
- Token cost: 13,000 input · 5,000 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Equity Proxy & HTTP Layer|Equity Proxy & HTTP Layer]]
- [[_COMMUNITY_Architecture Docs & Nginx Config|Architecture Docs & Nginx Config]]
- [[_COMMUNITY_MCP Server Tools|MCP Server Tools]]
- [[_COMMUNITY_Data Fetching & Formatting|Data Fetching & Formatting]]
- [[_COMMUNITY_Health Check System|Health Check System]]
- [[_COMMUNITY_IPO Data Source|IPO Data Source]]
- [[_COMMUNITY_NCD Bond Data Source|NCD Bond Data Source]]
- [[_COMMUNITY_Precious Metals Source|Precious Metals Source]]
- [[_COMMUNITY_Notification Delivery|Notification Delivery]]
- [[_COMMUNITY_MCP Equity Functions|MCP Equity Functions]]
- [[_COMMUNITY_Report Formatter|Report Formatter]]
- [[_COMMUNITY_Data Orchestration|Data Orchestration]]
- [[_COMMUNITY_Secondary Bonds Source|Secondary Bonds Source]]
- [[_COMMUNITY_US Fear & Greed Source|US Fear & Greed Source]]
- [[_COMMUNITY_FastAPI App & Routing|FastAPI App & Routing]]
- [[_COMMUNITY_Nginx Architecture Diagram|Nginx Architecture Diagram]]
- [[_COMMUNITY_Configuration & Settings|Configuration & Settings]]
- [[_COMMUNITY_Data Sources Package|Data Sources Package]]
- [[_COMMUNITY_Telegram Notifier|Telegram Notifier]]
- [[_COMMUNITY_Pydantic Models|Pydantic Models]]
- [[_COMMUNITY_Metals Rationale|Metals Rationale]]
- [[_COMMUNITY_Metals Rationale Alt|Metals Rationale Alt]]
- [[_COMMUNITY_Fear Greed Rationale|Fear Greed Rationale]]
- [[_COMMUNITY_Healthcheck Status|Healthcheck Status]]
- [[_COMMUNITY_Investable Bonds Endpoint|Investable Bonds Endpoint]]
- [[_COMMUNITY_US Index Endpoint|US Index Endpoint]]
- [[_COMMUNITY_Metals Endpoint|Metals Endpoint]]
- [[_COMMUNITY_IPO Endpoint|IPO Endpoint]]
- [[_COMMUNITY_Settings Config Node|Settings Config Node]]
- [[_COMMUNITY_Watchlist Config|Watchlist Config]]
- [[_COMMUNITY_Volume Formatter|Volume Formatter]]
- [[_COMMUNITY_Turnover Formatter|Turnover Formatter]]
- [[_COMMUNITY_Email Sender|Email Sender]]
- [[_COMMUNITY_httpx Dependency|httpx Dependency]]
- [[_COMMUNITY_requests Dependency|requests Dependency]]

## God Nodes (most connected - your core abstractions)
1. `RPi Market Notifier` - 19 edges
2. `run_health_check()` - 13 edges
3. `fetch_ipos()` - 12 edges
4. `fetch_all_data()` - 10 edges
5. `run_health_check` - 10 edges
6. `daily_job()` - 9 edges
7. `fetch_ncds()` - 9 edges
8. `fetch_secondary_bonds()` - 8 edges
9. `fetch_all_data` - 8 edges
10. `send_heartbeat_telegram()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `mood_indicator()` --calls--> `fetch_mmi()`  [INFERRED]
  main.py → data/sources/mmi.py
- `ipo()` --calls--> `fetch_ipos()`  [INFERRED]
  main.py → data/sources/ipo.py
- `FastApiMCP mount` --semantically_similar_to--> `FastMCP RPI MCP server`  [INFERRED] [semantically similar]
  main.py → mcp_server.py
- `main()` --calls--> `run_health_check()`  [INFERRED]
  main.py → healthcheck.py
- `main()` --calls--> `print_health_report()`  [INFERRED]
  main.py → healthcheck.py

## Hyperedges (group relationships)
- **MCP tools → FastAPI proxy → Upstream equity API pipeline** — mcp_server_get_fundamentals, mcp_server_bulk_equity_helper, mcp_server_equity_helper, proxy_reports_route, proxy_endpoint_enum [INFERRED 0.90]
- **Scheduler, Health Check, and Heartbeat notification loop** — scheduler_start_scheduler, healthcheck_run_health_check, healthcheck_send_heartbeat_telegram, healthcheck_start_health_server [EXTRACTED 0.95]
- **FastAPI app exposes REST and MCP interfaces simultaneously** — main_app, main_mcp, mcp_server_mcp, urls_router [INFERRED 0.85]
- **Market Data Aggregation Pipeline** — fetcher_fetch_all_data, formatter_format_telegram_report, formatter_format_email_report, summary_generate_summary [EXTRACTED 1.00]
- **Notification Delivery Flow** — formatter_format_telegram_report, formatter_format_email_report, telegram_notifier_send_telegram, email_notifier_send_email [INFERRED 0.85]
- **Fixed Income Quality Filter Pipeline** — ncd_fetch_ncds, secondary_bonds_fetch_secondary_bonds, rating_filter_pattern [INFERRED 0.90]
- **Dual MCP Implementation Stack** — requirements_fastmcp, requirements_fastapi_mcp, claude_two_mcp_implementations [EXTRACTED 1.00]
- **Nginx Reverse Proxy Routing Architecture** — nginx_dockercompose, readme_nginx_proxy, readme_ngrok_tunnel [EXTRACTED 1.00]
- **Notification Delivery Stack** — readme_multi_channel_delivery, requirements_python_telegram_bot, readme_apscheduler_trigger [INFERRED 0.85]
- **Nginx Reverse Proxy Routing to Backend Services** — nginx_architecture_nginx, nginx_architecture_service_a, nginx_architecture_service_b, nginx_architecture_service_n [EXTRACTED 1.00]
- **External Access Chain via ngrok and Nginx** — nginx_architecture_external_traffic, nginx_architecture_ngrok_tunnel, nginx_architecture_nginx [EXTRACTED 1.00]
- **Backend Microservices Pool Served by Nginx** — nginx_architecture_service_a, nginx_architecture_service_b, nginx_architecture_service_n [EXTRACTED 1.00]

## Communities (41 total, 18 thin omitted)

### Community 0 - "Equity Proxy & HTTP Layer"
Cohesion: 0.07
Nodes (37): BaseHTTPRequestHandler, Enum, Endpoint, reports(), check_api_mmi(), check_api_quotes(), check_email(), check_last_run() (+29 more)

### Community 1 - "Architecture Docs & Nginx Config"
Cohesion: 0.08
Nodes (33): Add New Data Source Pattern, Equity Proxy Endpoint Enum, Dual MCP Implementation Strategy, nginx:alpine Docker Image, nginx.conf Volume Mount, Nginx Docker Compose Configuration, AI Insights Feature, APScheduler Cron Trigger (+25 more)

### Community 2 - "MCP Server Tools"
Cohesion: 0.09
Nodes (30): _bulk_equity(), _equity(), get_about_company(), get_company_research_links(), get_dividend_history(), get_full_company_snapshot(), get_fundamentals(), get_investable_bonds() (+22 more)

### Community 3 - "Data Fetching & Formatting"
Cohesion: 0.11
Nodes (25): fetch_all_data, _arrow (helper), format_email_report, _format_fii (helper), format_telegram_report, fetch_ipos, IPOData, Market Data Dict Pattern (+17 more)

### Community 4 - "Health Check System"
Cohesion: 0.11
Nodes (22): check_api_mmi, check_api_quotes, check_email, check_last_run, check_system, check_telegram, format_heartbeat_message, HealthHandler (+14 more)

### Community 5 - "IPO Data Source"
Cohesion: 0.14
Nodes (15): _clean_date(), _count_fires(), _detect_status(), fetch_ipos(), _get_fy(), IPOData, _parse_gmp_value(), IPO Listings — Equity IPOs with GMP data from InvestorGain. (+7 more)

### Community 6 - "NCD Bond Data Source"
Cohesion: 0.13
Nodes (15): fetch_ncds(), _format_rating(), _freq_label(), _is_trusted_a_series(), NCDData, NCDSeriesData, _parse_date(), NCD IPO Listings — Open NCD IPOs from GoldenPi. (+7 more)

### Community 7 - "Precious Metals Source"
Cohesion: 0.15
Nodes (13): metals(), fetch_precious_metals(), gold(), MetalData, palladium(), platinum(), PreciousMetalsSnapshot, Precious Metals — Gold, Silver, Platinum, Palladium from Kitco. (+5 more)

### Community 8 - "Notification Delivery"
Cohesion: 0.13
Nodes (14): Send an individual HTML email to each receiver — fully private, no BCC visible., send_email(), Send a message via Telegram bot (async)., Send a Telegram message (sync wrapper)., _send(), send_telegram(), Save the last run status to a JSON file., save_run_status() (+6 more)

### Community 9 - "MCP Equity Functions"
Cohesion: 0.16
Nodes (18): _bulk_equity helper, _equity helper, FUNDAMENTALS endpoint bundle, get_about_company tool, get_company_research_links tool, get_dividend_history tool, get_full_company_snapshot tool, get_fundamentals tool (+10 more)

### Community 10 - "Report Formatter"
Cohesion: 0.15
Nodes (15): _arrow(), format_email_report(), _format_fii(), format_telegram_report(), _format_turnover(), _format_volume(), Format volume in Indian numbering (Cr / L / K)., Format an HTML email with market data. (+7 more)

### Community 11 - "Data Orchestration"
Cohesion: 0.14
Nodes (11): fetch_all_data(), Data Fetcher — Orchestrator that calls all modular data sources.  Each source li, Master fetch — calls all configured data sources., fetch_mmi(), MMIData, Market Mood Index — Fear & Greed gauge for Indian markets (TickerTape)., Fetch Market Mood Index from TickerTape., fetch_quotes() (+3 more)

### Community 12 - "Secondary Bonds Source"
Cohesion: 0.17
Nodes (12): investable_bonds(), BondData, fetch_secondary_bonds(), _is_trusted_a_series(), _parse_coupon(), _parse_yield(), Secondary Bond Market — Bond listings from IndiaBonds., Single bond/NCD from the secondary market. (+4 more)

### Community 13 - "US Fear & Greed Source"
Cohesion: 0.16
Nodes (10): us_index(), fetch_us_fear_greed(), _parse_sub(), US Fear & Greed Index — CNN Business Fear & Greed Index., Individual Fear & Greed sub-indicator., CNN Fear & Greed Index data., Parse a sub-indicator from the API response., Fetch CNN Fear & Greed Index. (+2 more)

### Community 14 - "FastAPI App & Routing"
Cohesion: 0.15
Nodes (15): ticker_router APIRouter, equity urls router, FastAPI app, FastApiMCP mount, mcp_client main, get_investable_bonds tool, get_ipo_data tool, get_metals_data tool (+7 more)

### Community 15 - "Nginx Architecture Diagram"
Cohesion: 0.53
Nodes (6): External Internet Traffic, Nginx Proxy on Port 2001, ngrok Static IP Tunnel, Service A on Port 8005 (svc1_name/v1/), Service B on Port 8006 (svc2_name/v1/), Service N (svc(n)_name/v1/)

### Community 16 - "Configuration & Settings"
Cohesion: 0.4
Nodes (4): _parse_bool(), _parse_tickers(), Parse TICKERS env var into list of {sid, name} dicts., Parse a boolean from env var string.

## Knowledge Gaps
- **143 isolated node(s):** `Save the last run status to a JSON file.`, `Load the last run status.`, `Check if MMI API is reachable and returning valid data.`, `Check if Quotes API is reachable with a test ticker.`, `Check Telegram bot token validity and chat reachability.` (+138 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_all_data()` connect `Data Orchestration` to `IPO Data Source`, `NCD Bond Data Source`, `Precious Metals Source`, `Notification Delivery`, `Secondary Bonds Source`, `US Fear & Greed Source`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `daily_job()` connect `Notification Delivery` to `Report Formatter`, `Data Orchestration`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `fetch_ipos()` connect `IPO Data Source` to `Notification Delivery`, `Equity Proxy & HTTP Layer`, `Data Orchestration`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `str` (e.g. with `check_api_mmi()` and `check_api_quotes()`) actually correct?**
  _`str` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `run_health_check()` (e.g. with `periodic_health_check()` and `main()`) actually correct?**
  _`run_health_check()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `fetch_ipos()` (e.g. with `ipo()` and `fetch_all_data()`) actually correct?**
  _`fetch_ipos()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `fetch_all_data()` (e.g. with `daily_job()` and `fetch_mmi()`) actually correct?**
  _`fetch_all_data()` has 8 INFERRED edges - model-reasoned connections that need verification._