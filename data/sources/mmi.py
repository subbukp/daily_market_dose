"""Market Mood Index — Fear & Greed gauge for Indian markets (TickerTape)."""

import requests
from dataclasses import dataclass
from typing import Optional

from config.settings import MMI_API


@dataclass
class MMIData:
    value: float            # Current MMI (0=Extreme Fear, 100=Extreme Greed)
    raw: float
    nifty: float
    vix: float
    fii: float
    gold: float
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


def fetch_mmi() -> Optional[MMIData]:
    """Fetch Market Mood Index from TickerTape."""
    if not MMI_API:
        print("⏭️  MMI skipped — MMI_API not set in .env")
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(MMI_API, headers=headers, timeout=15)
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





