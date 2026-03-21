"""Secondary Bond Market — Bond listings from IndiaBonds."""

import re
import requests
from dataclasses import dataclass
from typing import List, Optional

from config.settings import SECONDARY_BONDS_API


# ─── Filters ───
TRUSTED_AGENCIES = {"ICRA", "CRISIL", "CARE"}
MINIMUM_RATING_RANK = 7   # A- and above
MIN_YIELD_PCT = 10.0

_RATING_RANKS = {
    "AAA": 1,
    "AA+": 2, "AA(CE)": 2,
    "AA": 3,
    "AA-": 4,
    "A+": 5,
    "A": 6,
    "A-": 7,
}


@dataclass
class BondData:
    """Single bond/NCD from the secondary market."""
    name: str
    isin: str
    bond_type: str              # Secured, Unsecured, etc.
    price: float
    yield_pct: float
    coupon_rate: float
    maturity_date: str
    credit_rating: str          # e.g. "CARE: A-"
    rating_agency: str
    rating_value: str
    interest_freq: str          # Monthly, Quarterly, etc.
    secured: bool

    @property
    def yield_display(self) -> str:
        return f"{self.yield_pct:.2f}%"

    @property
    def coupon_display(self) -> str:
        return f"{self.coupon_rate:.2f}%"


def _parse_yield(yield_str: str) -> float:
    """Parse yield string like '12.1619%' to float."""
    if not yield_str:
        return 0.0
    return float(yield_str.replace("%", "").strip())


def _parse_coupon(coupon_str: str) -> float:
    """Parse coupon string like '11.6500%' to float."""
    if not coupon_str:
        return 0.0
    return float(coupon_str.replace("%", "").strip())


def _is_trusted_a_series(agency: str, rating: str) -> bool:
    """Check if agency is trusted and rating is A-series or above."""
    if not agency or not rating:
        return False
    agency_upper = agency.strip().upper()
    if agency_upper not in TRUSTED_AGENCIES:
        return False
    core = re.sub(r"\s*\((?!CE)[^)]*\)", "", rating).strip()
    rank = _RATING_RANKS.get(core)
    return rank is not None and rank <= MINIMUM_RATING_RANK


def fetch_secondary_bonds(top_n: int = 5, filter: bool = True) -> List[BondData]:
    """Fetch top secondary market bonds from IndiaBonds, sorted by yield."""
    if not SECONDARY_BONDS_API:
        print("⏭️  Secondary Bonds skipped — SECONDARY_BONDS_API not set in .env")
        return []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
            "Accept": "application/json",
        }
        resp = requests.get(SECONDARY_BONDS_API, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()

        bonds_list = payload.get("bond_list", [])

        bonds = []
        skipped = 0

        for b in bonds_list:
            yield_pct = _parse_yield(b.get("yield_value", ""))
            agency = b.get("rating_agency", "")
            rating = b.get("rating", "")

            if filter:
                # ── Filter 1: Minimum yield ──
                if yield_pct < MIN_YIELD_PCT:
                    skipped += 1
                    continue

                # ── Filter 2: Trusted agency + A-series rating ──
                if not _is_trusted_a_series(agency, rating):
                    skipped += 1
                    continue

            # ── Passed filters ──
            name = b.get("issuer_name", "Unknown")
            isin = b.get("isin", "N/A")
            price = float(b.get("price", 0) or 0)
            coupon_rate = _parse_coupon(b.get("coupon_rate", ""))
            maturity_date = b.get("maturity_date", "N/A") or "N/A"
            freq = b.get("frequency", "N/A") or "N/A"
            security_type = b.get("security_type", "")
            bond_type = b.get("type_of_bond", "")
            credit_rating = b.get("rating_combined", f"{agency} {rating}")

            bonds.append(BondData(
                name=name,
                isin=isin,
                bond_type=bond_type,
                price=price,
                yield_pct=yield_pct,
                coupon_rate=coupon_rate,
                maturity_date=maturity_date,
                credit_rating=credit_rating,
                rating_agency=agency,
                rating_value=rating,
                interest_freq=freq.title(),
                secured=security_type.lower() == "secured",
            ))
            

            if len(bonds) >= top_n:
                break

        print(f"📊 Secondary Bonds: {len(bonds)} passed filters, {skipped} skipped "
              f"(min yield: {MIN_YIELD_PCT}%, agencies: {', '.join(TRUSTED_AGENCIES)}, rating: A- and above)")

        bonds.sort(key=lambda x: x.yield_pct, reverse=True)
        return bonds

    except Exception as e:
        print(f"❌ Secondary Bonds fetch error: {e}")
        return []
