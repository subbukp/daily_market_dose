## What this project does

RPi Market Notifier aggregates Indian market data (Market Mood Index, stock quotes, IPOs, NCDs, bonds, precious metals, US Fear & Greed) and delivers daily reports via Telegram and Email. It also exposes a FastAPI REST server and an MCP server so AI assistants can query market data as tools.

## Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in credentials

# Run once (dry run — no notifications sent)
python main.py --test

# Run once and send notifications
python main.py

# Health check
python main.py --health

# Scheduler (Mon–Fri cron at configured time)
python scheduler.py
python scheduler.py --with-health         # also starts HTTP health endpoint on :8080
python scheduler.py --with-health --port 9090

# API server (dev)
uvicorn main:app --host 0.0.0.0 --port 8005

# API server (production, multi-worker)
gunicorn main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8005

# MCP server (runs on :8006)
python mcp_server.py

# Nginx reverse proxy (Docker)
cd nginx && docker compose up -d
```

## Architecture

### Data flow

`daily_job()` in [main.py](main.py) is the central orchestrator:
1. Calls `fetch_all_data()` in [data/fetcher.py](data/fetcher.py), which fans out to all source modules in [data/sources/](data/sources/) in parallel
2. Passes the aggregated dict to [data/formatter.py](data/formatter.py) to produce a Telegram Markdown report and an HTML email report
3. [data/summary.py](data/summary.py) generates AI-written market insights that are embedded in the formatter output
4. Sends via [notifications/telegram_notifier.py](notifications/telegram_notifier.py) and [notifications/email_notifier.py](notifications/email_notifier.py) based on `CHANNEL_TELEGRAM` / `CHANNEL_EMAIL` flags

### Ports and routing

| Port | Service |
|------|---------|
| 8005 | FastAPI REST (`main.py`) |
| 8006 | MCP server (`mcp_server.py`) |
| 2001 | Nginx reverse proxy (Docker) |

Nginx routes `/market/*` → `:8005` and `/market-mcp/*` → `:8006`, fronted by ngrok for external access.

### MCP layer (two implementations)

There are two separate MCP implementations:
- **[mcp_server.py](mcp_server.py)** — standalone `fastmcp`-based server, runs on `:8006`. Exposes rich per-company tools (`get_fundamentals`, `get_valuation`, `get_ownership`, `get_news_and_research`, `get_full_company_snapshot`) plus market-wide tools. Uses `company_id` (integer) as the identifier, proxied through the equity endpoints.
- **`main.py`** — also mounts an MCP layer via `fastapi-mcp` (`FastApiMCP(app).mount()`), which auto-exposes the FastAPI routes as MCP tools.

### Equity proxy

[equity/proxy.py](equity/proxy.py) defines an `Endpoint` enum mapping short names (e.g. `pnl_ratio`, `quarterly_result`) to full upstream query strings. The route `GET /equity/{path}/{company_id}` looks up the enum, appends `companyId=`, and proxies to `BASE_URL` from env. Adding a new equity endpoint means adding a value to `Endpoint` — no other changes needed.

### Configuration

All config lives in [config/settings.py](config/settings.py) loaded from `.env` via `python-dotenv`. Key variables:

- `TICKERS` — watchlist in `SID:Name` format (SID from tickertape.in URL slug, e.g. `RELI:Reliance Industries`)
- `BASE_URL` — upstream equity data API base URL (used by the proxy)
- All external API endpoints (`MMI_API`, `QUOTES_API`, `IPO_API`, etc.) are configured in `.env`, not hardcoded
- `CHANNEL_TELEGRAM` / `CHANNEL_EMAIL` — toggle delivery channels without code changes

### Adding a new data source

1. Create `data/sources/<name>.py` with a `fetch_<name>()` function returning a typed dataclass or dict
2. Add it to `fetch_all_data()` in [data/fetcher.py](data/fetcher.py)
3. Add formatting in [data/formatter.py](data/formatter.py) for both Telegram and Email sections
4. Optionally expose as a FastAPI endpoint in [main.py](main.py) and an MCP tool in [mcp_server.py](mcp_server.py)

