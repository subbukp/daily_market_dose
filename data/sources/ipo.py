"""IPO Listings — Equity IPOs with GMP data from InvestorGain."""

import re
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from config.settings import IPO_API


# ─── Filters ───
MIN_GMP_PERCENT = 20.0      # Only show IPOs with GMP >= 20%
MIN_FIRE_RATING = 2         # Minimum 🔥🔥 (2 fires) rating

# Fire rating guide (from InvestorGain):
#   🔥       = 1 fire  = Weak / risky
#   🔥🔥     = 2 fires = Decent
#   🔥🔥🔥   = 3 fires = Good
#   🔥🔥🔥🔥 = 4 fires = Very Good
#   🔥🔥🔥🔥🔥 = 5 fires = Excellent


@dataclass
class IPOData:
    company: str
    category: str               # "IPO" or "SME"
    open_date: str
    close_date: str
    listing_date: str
    boa_date: str               # Basis of allotment date
    price: str                  # Issue price (₹)
    issue_size_cr: str
    lot_size: str
    pe_ratio: str
    gmp_value: str              # GMP in ₹ (e.g. "8")
    gmp_percent: float          # GMP as % (e.g. 0.89)
    subscription: str           # e.g. "0.03x"
    fire_rating: int            # Number of 🔥 (1-5)
    has_anchor: bool            # Anchor investor allocation
    status: str                 # "O" = Open, "U" = Upcoming, "C" = Closed/Allotted
    is_open: bool
    is_upcoming: bool

    @property
    def status_emoji(self) -> str:
        if self.is_open:
            return "🟢"
        elif self.is_upcoming:
            return "🔜"
        return "⚪"

    @property
    def gmp_display(self) -> str:
        if self.gmp_percent > 0:
            return f"🟢 +{self.gmp_percent:.1f}% (₹{self.gmp_value})"
        elif self.gmp_percent < 0:
            return f"🔴 {self.gmp_percent:.1f}% (₹{self.gmp_value})"
        return "⚪ 0%"

    @property
    def fire_display(self) -> str:
        return "🔥" * self.fire_rating if self.fire_rating > 0 else "—"

    @property
    def anchor_display(self) -> str:
        return "✅" if self.has_anchor else "❌"


def _strip_html(text: str) -> str:
    """Strip HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _clean_date(date_html: str) -> str:
    """Extract just the date from HTML like '9-Feb<small ...>GMP: 8</small>'."""
    if not date_html:
        return "N/A"
    # Remove all HTML tags first
    text = re.sub(r"<[^>]+>", " ", date_html).strip()
    # Take only the first date-like part (e.g. "9-Feb" from "9-Feb GMP: 8")
    match = re.match(r"(\d{1,2}-\w{3})", text)
    if match:
        return match.group(1)
    return text.split()[0] if text else "N/A"


def _count_fires(rating_html: str) -> int:
    """Count 🔥 emojis in the Rating HTML field.
    They appear as &#128293; or the actual emoji character."""
    if not rating_html:
        return 0
    # Count HTML entity &#128293;
    count = rating_html.count("&#128293;")
    if count > 0:
        return count
    # Count actual emoji 🔥
    count = rating_html.count("🔥")
    return count


def _parse_gmp_value(gmp_html: str) -> str:
    """Extract GMP ₹ value from HTML like '₹<b>8</b> (0.89%)'."""
    if not gmp_html:
        return "--"
    match = re.search(r"<b>(.*?)</b>", gmp_html)
    if match:
        return match.group(1).strip()
    return "--"


def _detect_status(row: dict) -> str:
    """Detect IPO status from the Name field badges.
    O = Open, U = Upcoming, C = Closed/Allotted."""
    name_html = row.get("Name", "")
    if "bg-success" in name_html and ">O<" in name_html:
        return "O"
    elif "bg-warning" in name_html and ">U<" in name_html:
        return "U"
    elif "bg-primary" in name_html and ">C<" in name_html:
        return "C"
    # Fallback: check highlight row color
    highlight = row.get("~Highlight_Row", "")
    if "green" in highlight:
        return "O"
    elif "yellow" in highlight:
        return "U"
    return "C"


def _get_fy() -> tuple:
    now = datetime.now()
    year, month = now.year, now.month
    if month >= 4:
        fy = f"{year}-{str(year + 1)[-2:]}"
    else:
        fy = f"{year - 1}-{str(year)[-2:]}"
    return year, fy, month


def fetch_ipos() -> List[IPOData]:
    """Fetch IPOs with GMP data from InvestorGain. Filters by GMP% and rating."""
    if not IPO_API:
        print("⏭️  IPO skipped — IPO_API not set in .env")
        return []
    try:
        year, fy, month = _get_fy()
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

        all_ipos = []
        filtered = []
        skipped = 0

        for row in payload.get("reportTableData", []):
            company = row.get("~ipo_name", _strip_html(row.get("Name", "")))
            category = row.get("~IPO_Category", "IPO")
            status = _detect_status(row)

            gmp_pct = float(row.get("~gmp_percent_calc", 0) or 0)
            gmp_val = _parse_gmp_value(row.get("GMP", ""))
            fire_rating = _count_fires(row.get("Rating", ""))
            subscription = _strip_html(row.get("Sub", "-"))
            pe_ratio = str(row.get("~P/E", "N/A"))
            price = str(row.get("Price (₹)", "N/A")).strip()
            issue_size = str(row.get("IPO Size (₹ in cr)", "N/A")).strip()
            lot_size = str(row.get("Lot", "N/A")).strip()

            open_date = _clean_date(row.get("Open", ""))
            close_date = _clean_date(row.get("Close", ""))
            listing_date = _clean_date(row.get("Listing", ""))
            boa_date = _clean_date(row.get("BoA Dt", ""))
            has_anchor = "✅" in row.get("Anchor", "")

            is_open = status == "O"
            is_upcoming = status == "U"

            ipo = IPOData(
                company=company,
                category=category,
                open_date=open_date,
                close_date=close_date,
                listing_date=listing_date,
                boa_date=boa_date,
                price=price,
                issue_size_cr=issue_size,
                lot_size=lot_size,
                pe_ratio=pe_ratio,
                gmp_value=gmp_val,
                gmp_percent=gmp_pct,
                subscription=subscription,
                fire_rating=fire_rating,
                has_anchor=has_anchor,
                status=status,
                is_open=is_open,
                is_upcoming=is_upcoming,
            )

            all_ipos.append(ipo)

            # ── Apply filters: GMP >= 20% AND rating >= 2 fires ──
            if gmp_pct >= MIN_GMP_PERCENT and fire_rating >= MIN_FIRE_RATING:
                filtered.append(ipo)
            else:
                skipped += 1

        # Sort: open first, then upcoming, then by GMP% descending
        filtered.sort(key=lambda x: (not x.is_open, not x.is_upcoming, -x.gmp_percent))

        total = len(all_ipos)
        passed = len(filtered)
        print(f"🏷️  IPOs: {passed} passed filters out of {total} "
              f"(min GMP: {MIN_GMP_PERCENT}%, min rating: {'🔥' * MIN_FIRE_RATING})")

        return filtered

    except Exception as e:
        print(f"❌ IPO fetch error: {e}")
        return []
