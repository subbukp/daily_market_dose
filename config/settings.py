import os
from dotenv import load_dotenv

load_dotenv()


def _parse_bool(value: str, default: bool = True) -> bool:
    """Parse a boolean from env var string."""
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes", "on")


# ─── Notification Channels ───
# Toggle which channels are active (true/false in .env)
CHANNEL_TELEGRAM = _parse_bool(os.getenv("CHANNEL_TELEGRAM"), default=True)
CHANNEL_EMAIL = _parse_bool(os.getenv("CHANNEL_EMAIL"), default=True)

# ─── Telegram ───
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ─── Email ───
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# ─── API Endpoints (all from .env) ───
MMI_API = os.getenv("MMI_API")
QUOTES_API = os.getenv("QUOTES_API")
IPO_API = os.getenv("IPO_API")

# ─── Watchlist (from .env) ───
# Format in .env: TICKERS=SID:Display Name,SID:Display Name,...
# e.g. TICKERS=RELI:Reliance Industries,TCS:TCS,INFY:Infosys
#
# Find SIDs on tickertape.in URL for each stock:
# https://www.tickertape.in/stocks/nestle-india-NSEN → sid = "NSEN"


def _parse_tickers(env_value: str) -> list:
    """Parse TICKERS env var into list of {sid, name} dicts."""
    tickers = []
    if not env_value:
        return tickers
    for entry in env_value.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            sid, name = entry.split(":", 1)
            tickers.append({"sid": sid.strip(), "name": name.strip()})
        else:
            # If no name given, use SID as name
            tickers.append({"sid": entry.strip(), "name": entry.strip()})
    return tickers


WATCHLIST = _parse_tickers(os.getenv("TICKERS", ""))

# ─── Schedule ───
NOTIFY_HOUR = int(os.getenv("NOTIFY_HOUR", "18"))
NOTIFY_MINUTE = int(os.getenv("NOTIFY_MINUTE", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# ─── Heartbeat ───
HEARTBEAT_INTERVAL_HOURS = int(os.getenv("HEARTBEAT_INTERVAL_HOURS", "1"))
HEARTBEAT_ENABLED = _parse_bool(os.getenv("HEARTBEAT_ENABLED"), default=True)

