"""Precious Metals — Gold, Silver, Platinum, Palladium from Kitco."""

import requests
from dataclasses import dataclass
from typing import List, Optional

from config.settings import PRECIOUS_METALS_API


@dataclass
class MetalData:
    """Single precious metal price data."""
    commodity: str              # Gold, Silver, Platinum, Palladium
    price: float                # Current bid price (USD)
    change: float               # Total change ($)
    change_pct: float           # Total change (%)
    change_usd: float           # Change due to USD movement
    change_usd_pct: float
    change_trade: float         # Change due to trading
    change_trade_pct: float
    currency: str
    time: str                   # Last update time

    @property
    def direction_emoji(self) -> str:
        if self.change_pct > 0:
            return "🟢"
        elif self.change_pct < 0:
            return "🔴"
        return "⚪"

    @property
    def change_display(self) -> str:
        sign = "+" if self.change >= 0 else ""
        return f"{sign}${self.change:.2f} ({sign}{self.change_pct:.2f}%)"


@dataclass
class PreciousMetalsSnapshot:
    """All precious metals + computed ratios."""
    metals: List[MetalData]

    def get(self, commodity: str) -> Optional[MetalData]:
        """Get a specific metal by name."""
        for m in self.metals:
            if m.commodity.lower() == commodity.lower():
                return m
        return None

    @property
    def gold(self) -> Optional[MetalData]:
        return self.get("Gold")

    @property
    def silver(self) -> Optional[MetalData]:
        return self.get("Silver")

    @property
    def platinum(self) -> Optional[MetalData]:
        return self.get("Platinum")

    @property
    def palladium(self) -> Optional[MetalData]:
        return self.get("Palladium")

    @property
    def gold_silver_ratio(self) -> Optional[float]:
        """Gold/Silver ratio — historically ~60-80 is normal."""
        g, s = self.gold, self.silver
        if g and s and s.price > 0:
            return round(g.price / s.price, 2)
        return None

    @property
    def gold_silver_signal(self) -> str:
        """Interpret the Gold/Silver ratio."""
        ratio = self.gold_silver_ratio
        if ratio is None:
            return ""
        if ratio > 80:
            return "📈 Silver undervalued (ratio high)"
        elif ratio < 60:
            return "📉 Silver overvalued (ratio low)"
        return "⚖️ Normal range"


def fetch_precious_metals() -> Optional[PreciousMetalsSnapshot]:
    """Fetch precious metals prices from Kitco."""
    if not PRECIOUS_METALS_API:
        print("⏭️  Precious Metals skipped — PRECIOUS_METALS_API not set in .env")
        return None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(PRECIOUS_METALS_API, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()

        if not payload.get("success"):
            print("⚠️  Precious Metals API returned success=false")
            return None

        # Only include Gold and Silver
        INCLUDE = {"Gold", "Silver"}

        metals = []
        for item in payload.get("data", []):
            if item.get("commodity") not in INCLUDE:
                continue

            bid = item.get("lastBid", {})
            total = item.get("totalChange", {})
            usd = item.get("changeDueToUSD", {})
            trade = item.get("changeDueToTrade", {})

            metals.append(MetalData(
                commodity=item.get("commodity", "Unknown"),
                price=float(bid.get("bidVal", 0)),
                change=float(total.get("changeVal", 0)),
                change_pct=float(total.get("percentageVal", 0)),
                change_usd=float(usd.get("changeVal", 0)),
                change_usd_pct=float(usd.get("percentageVal", 0)),
                change_trade=float(trade.get("changeVal", 0)),
                change_trade_pct=float(trade.get("percentageVal", 0)),
                currency=bid.get("currency", "USD"),
                time=bid.get("originalTime", ""),
            ))

        snapshot = PreciousMetalsSnapshot(metals=metals)
        g = snapshot.gold
        s = snapshot.silver
        ratio = snapshot.gold_silver_ratio
        print(f"🪙 Precious Metals: Gold=${g.price:,.2f} Silver=${s.price:,.2f} "
              f"Au/Ag={ratio}" if g and s and ratio else "🪙 Precious Metals: fetched")
        return snapshot

    except Exception as e:
        print(f"❌ Precious Metals fetch error: {e}")
        return None

