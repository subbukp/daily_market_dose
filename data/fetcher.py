import re
import requests
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional

import sys
import os

# Add project root to path so config can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MMI_API, QUOTES_API, IPO_API, WATCHLIST


# ─── Data Models ───

@dataclass
class MMIData:
    """Market Mood Index — Fear & Greed gauge for Indian markets."""
    value: float            # Current MMI (0=Extreme Fear, 100=Extreme Greed)
    raw: float
    nifty: float
    vix: float
    fii: float              # FII net flow
    gold: float
    # Comparisons
    last_day_value: float
    last_week_value: float
    last_month_value: float
    last_year_value: float
    timestamp: str

    @property
    def mood(self) -> str:
        if self.value <= 20:
            return "😱 Extreme Fear"
        elif self.value <= 40:
            return "😰 Fear"
        elif self.value <= 60:
            return "😐 Neutral"
        elif self.value <= 80:
            return "😀 Greed"
        else:
            return "🤑 Extreme Greed"

    @property
    def day_change(self) -> float:
        return round(self.value - self.last_day_value, 2)


@dataclass
class QuoteData:
    """Single ticker quote from TickerTape."""
    sid: str
    name: str
    price: float
    open: float
    high: float
    low: float
    close: float            # Previous close
    change: float           # Absolute change
    day_change_pct: float   # Daily %
    week_change_pct: float  # Weekly %
    month_change_pct: float # Monthly %
    volume: int
    turnover: float
    away_52w_high: float    # % away from 52w high
    away_52w_low: float     # % away from 52w low
    low_52w: float
    high_52w: float


# ─── Fetchers ───

def fetch_mmi() -> Optional[MMIData]:
    """Fetch Market Mood Index data from TickerTape."""
    if not MMI_API:
        print("⏭️  MMI skipped — MMI_API not set in .env")
        return None
    try:
        url = MMI_API
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()

        if not payload.get("success"):
            print("⚠️  MMI API returned success=false")
            return None

        d = payload["data"]
        return MMIData(
            value=round(d["currentValue"], 2),
            raw=round(d["raw"], 2),
            nifty=d["nifty"],
            vix=d["vix"],
            fii=d["fii"],
            gold=d["gold"],
            last_day_value=round(d["lastDay"]["indicator"], 2),
            last_week_value=round(d["lastWeek"]["indicator"], 2),
            last_month_value=round(d["lastMonth"]["indicator"], 2),
            last_year_value=round(d["lastYear"]["indicator"], 2),
            timestamp=d["date"],
        )
    except Exception as e:
        print(f"❌ MMI fetch error: {e}")
        return None


def fetch_quotes(sids: List[str]) -> List[QuoteData]:
    """Fetch live quotes for a list of TickerTape SIDs."""
    if not QUOTES_API:
        print("⏭️  Quotes skipped — QUOTES_API not set in .env")
        return []
    if not sids:
        return []

    try:
        base_url = QUOTES_API
        sid_param = ",".join(sids)
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(
            base_url,
            params={"sids": sid_param},
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()

        # Build a name lookup from WATCHLIST
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


# ─── IPO Data ───

@dataclass
class IPOData:
    """Single IPO listing from Chittorgarh."""
    company: str
    open_date: str
    close_date: str
    listing_date: str
    price_range: str
    issue_size_cr: str
    listing_at: str
    lead_manager: str
    is_open: bool           # Currently accepting applications
    is_upcoming: bool       # Not yet open
    is_listed: bool         # Already listed

    @property
    def status_emoji(self) -> str:
        if self.is_open:
            return "🟢"
        elif self.is_upcoming:
            return "🔜"
        elif self.is_listed:
            return "✅"
        return "⚪"

    @property
    def status_text(self) -> str:
        if self.is_open:
            return "Open Now"
        elif self.is_upcoming:
            return "Upcoming"
        elif self.is_listed:
            return "Listed"
        return ""


def _strip_html(text: str) -> str:
    """Strip HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _parse_date_str(date_str: str) -> Optional[date]:
    """Parse date string like 'Mon, Feb 09, 2026' into date object."""
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%a, %b %d, %Y").date()
    except ValueError:
        return None


def fetch_ipos() -> List[IPOData]:
    """Fetch current/upcoming IPO data from Chittorgarh."""
    if not IPO_API:
        print("⏭️  IPO skipped — IPO_API not set in .env")
        return []
    try:
        # Build URL with current year and financial year
        now = datetime.now()
        year = now.year
        month = now.month
        # Financial year: Apr 2025 – Mar 2026 = "2025-26"
        if month >= 4:
            fy = f"{year}-{str(year + 1)[-2:]}"
        else:
            fy = f"{year - 1}-{str(year)[-2:]}"

        url = IPO_API.format(year=year, fy=fy, month=month)

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("msg") != 1:
            print("⚠️  IPO API returned unexpected response")
            return []

        today = date.today()
        ipos = []

        for row in payload.get("reportTableData", []):
            company = _strip_html(row.get("Company", ""))
            open_date_str = row.get("Opening Date", "")
            close_date_str = row.get("Closing Date", "")
            listing_date_str = row.get("Listing Date", "")
            lead_manager = _strip_html(row.get("Left Lead Manager", ""))

            open_date = _parse_date_str(open_date_str)
            close_date = _parse_date_str(close_date_str)
            listing_date = _parse_date_str(listing_date_str)

            # Determine status
            is_open = False
            is_upcoming = False
            is_listed = False

            if open_date and close_date:
                if open_date <= today <= close_date:
                    is_open = True
                elif today < open_date:
                    is_upcoming = True

            if listing_date and listing_date <= today:
                is_listed = True
                is_open = False
                is_upcoming = False

            ipos.append(IPOData(
                company=company,
                open_date=open_date_str.strip(),
                close_date=close_date_str.strip(),
                listing_date=listing_date_str.strip() if listing_date_str.strip() else "TBD",
                price_range=row.get("Issue Price (Rs.)", "N/A").strip(),
                issue_size_cr=row.get("Total Issue Amount (Incl.Firm reservations) (Rs.cr.)", "N/A").strip(),
                listing_at=row.get("Listing at", "").strip(),
                lead_manager=lead_manager,
                is_open=is_open,
                is_upcoming=is_upcoming,
                is_listed=is_listed,
            ))

        # Sort: open first, then upcoming, then listed
        ipos.sort(key=lambda x: (not x.is_open, not x.is_upcoming, not x.is_listed))
        return ipos

    except Exception as e:
        print(f"❌ IPO fetch error: {e}")
        return []


def fetch_all_data() -> Dict:
    """Master fetch — grabs MMI + quotes + IPO data."""
    all_sids = [item["sid"] for item in WATCHLIST]

    if not all_sids:
        print("⚠️  No tickers configured. Set TICKERS in .env")

    return {
        "mmi": fetch_mmi(),
        "quotes": fetch_quotes(all_sids),
        "ipos": fetch_ipos(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


