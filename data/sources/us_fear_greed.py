"""US Fear & Greed Index — CNN Business Fear & Greed Index."""

import requests
from dataclasses import dataclass
from typing import Optional

from config.settings import US_FEAR_GREED_API


@dataclass
class SubIndicator:
    """Individual Fear & Greed sub-indicator."""
    name: str
    score: float        # 0-100
    rating: str         # extreme fear, fear, neutral, greed, extreme greed

    @property
    def emoji(self) -> str:
        r = self.rating.lower()
        if "extreme fear" in r:
            return "😱"
        elif "fear" in r:
            return "😰"
        elif "neutral" in r:
            return "😐"
        elif "extreme greed" in r:
            return "🤑"
        elif "greed" in r:
            return "😀"
        return "❓"


@dataclass
class USFearGreedData:
    """CNN Fear & Greed Index data."""
    score: float            # Current score (0-100)
    rating: str             # extreme fear, fear, neutral, greed, extreme greed
    previous_close: float
    previous_1_week: float
    previous_1_month: float
    previous_1_year: float
    timestamp: str
    # Sub-indicators
    market_momentum: Optional[SubIndicator] = None
    stock_price_strength: Optional[SubIndicator] = None
    stock_price_breadth: Optional[SubIndicator] = None
    put_call_options: Optional[SubIndicator] = None
    market_volatility: Optional[SubIndicator] = None
    junk_bond_demand: Optional[SubIndicator] = None
    safe_haven_demand: Optional[SubIndicator] = None

    @property
    def mood(self) -> str:
        r = self.rating.lower()
        if "extreme fear" in r:
            return "😱 Extreme Fear"
        elif "fear" in r:
            return "😰 Fear"
        elif "neutral" in r:
            return "😐 Neutral"
        elif "extreme greed" in r:
            return "🤑 Extreme Greed"
        elif "greed" in r:
            return "😀 Greed"
        return self.rating.title()

    @property
    def day_change(self) -> float:
        return round(self.score - self.previous_close, 2)

    @property
    def sub_indicators(self) -> list:
        """Return all sub-indicators as a list."""
        indicators = [
            ("Market Momentum", self.market_momentum),
            ("Stock Price Strength", self.stock_price_strength),
            ("Stock Price Breadth", self.stock_price_breadth),
            ("Put/Call Options", self.put_call_options),
            ("Market Volatility (VIX)", self.market_volatility),
            ("Junk Bond Demand", self.junk_bond_demand),
            ("Safe Haven Demand", self.safe_haven_demand),
        ]
        return [(name, ind) for name, ind in indicators if ind is not None]


def _parse_sub(data: dict, key: str, name: str) -> Optional[SubIndicator]:
    """Parse a sub-indicator from the API response."""
    sub = data.get(key)
    if sub and isinstance(sub, dict) and "score" in sub:
        return SubIndicator(
            name=name,
            score=float(sub.get("score", 0)),
            rating=sub.get("rating", "neutral"),
        )
    return None


def fetch_us_fear_greed() -> Optional[USFearGreedData]:
    """Fetch CNN Fear & Greed Index."""
    if not US_FEAR_GREED_API:
        print("⏭️  US Fear & Greed skipped — US_FEAR_GREED_API not set in .env")
        return None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        resp = requests.get(US_FEAR_GREED_API, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()

        fg = payload.get("fear_and_greed", {})
        if not fg:
            print("⚠️  US Fear & Greed API returned no data")
            return None

        result = USFearGreedData(
            score=round(float(fg.get("score", 0)), 1),
            rating=fg.get("rating", "neutral"),
            previous_close=round(float(fg.get("previous_close", 0)), 1),
            previous_1_week=round(float(fg.get("previous_1_week", 0)), 1),
            previous_1_month=round(float(fg.get("previous_1_month", 0)), 1),
            previous_1_year=round(float(fg.get("previous_1_year", 0)), 1),
            timestamp=fg.get("timestamp", ""),
            market_momentum=_parse_sub(payload, "market_momentum_sp500", "Market Momentum"),
            stock_price_strength=_parse_sub(payload, "stock_price_strength", "Stock Price Strength"),
            stock_price_breadth=_parse_sub(payload, "stock_price_breadth", "Stock Price Breadth"),
            put_call_options=_parse_sub(payload, "put_call_options", "Put/Call Options"),
            market_volatility=_parse_sub(payload, "market_volatility_vix", "Market Volatility"),
            junk_bond_demand=_parse_sub(payload, "junk_bond_demand", "Junk Bond Demand"),
            safe_haven_demand=_parse_sub(payload, "safe_haven_demand", "Safe Haven Demand"),
        )

        print(f"🇺🇸 US Fear & Greed: {result.score:.0f} ({result.rating})")
        return result

    except Exception as e:
        print(f"❌ US Fear & Greed fetch error: {e}")
        return None


