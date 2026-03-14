"""Stock Quotes — Live ticker prices from TickerTape."""

import requests
from dataclasses import dataclass
from typing import List

from config.settings import QUOTES_API, WATCHLIST


@dataclass
class QuoteData:
    sid: str
    name: str
    price: float
    open: float
    high: float
    low: float
    close: float
    change: float
    day_change_pct: float
    week_change_pct: float
    month_change_pct: float
    volume: int
    turnover: float
    away_52w_high: float
    away_52w_low: float
    low_52w: float
    high_52w: float


def fetch_quotes(sids: List[str]) -> List[QuoteData]:
    """Fetch live quotes for a list of TickerTape SIDs."""
    if not QUOTES_API:
        print("⏭️  Quotes skipped — QUOTES_API not set in .env")
        return []
    if not sids:
        return []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(
            QUOTES_API,
            params={"sids": ",".join(sids)},
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()

        name_map = {item["sid"]: item["name"] for item in WATCHLIST}

        quotes = []
        for q in payload.get("data", []):
            quotes.append(QuoteData(
                sid=q["sid"],
                name=name_map.get(q["sid"], q["sid"]),
                price=q.get("price", 0),
                open=q.get("o", 0),
                high=q.get("h", 0),
                low=q.get("l", 0),
                close=q.get("c", 0),
                change=q.get("change", 0),
                day_change_pct=q.get("dyChange", 0),
                week_change_pct=q.get("wkChange", 0),
                month_change_pct=q.get("mnChange", 0),
                volume=q.get("vol", 0),
                turnover=q.get("turnover", 0),
                away_52w_high=q.get("away52wH", 0),
                away_52w_low=q.get("away52wL", 0),
                low_52w=q.get("low52w", 0),
                high_52w=q.get("high52w", 0),
            ))
        return quotes
    except Exception as e:
        print(f"❌ Quotes fetch error: {e}")
        return []





