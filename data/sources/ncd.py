"""NCD IPO Listings — Open NCD IPOs from GoldenPi."""

import re
import requests
from dataclasses import dataclass, field
from typing import List, Optional

from config.settings import NCD_IPO_API, NCD_IPO_TOKEN


# ─── Default request body ───
DEFAULT_REQUEST_BODY = {
    "summaryOnly": False,
    "options": {"orderBy": "ytmc", "order": "desc"},
}

# ─── Filters ───
TRUSTED_AGENCIES = {"ICRA", "CRISIL", "CARE"}
MIN_YIELD_PCT = 10.0
MINIMUM_RATING_RANK = 7   # A- and above

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
class NCDSeriesData:
    """Single series/tranche within an NCD IPO."""
    series: str
    coupon_rate: float          # Coupon rate (%)
    yield_pct: float            # Yield to maturity/call (%)
    tenure_months: int
    face_value: float
    interest_freq: str          # Monthly, Quarterly, Annual, Cumulative
    min_lot_size: int
    secured: bool
    issue_size_cr: float        # In Crores
    coupon_type: str            # FIXED, COUPON_NOT_APPLICABLE (cumulative)

    @property
    def tenure_display(self) -> str:
        years = self.tenure_months // 12
        months = self.tenure_months % 12
        if years and months:
            return f"{years}y {months}m"
        elif years:
            return f"{years}y"
        return f"{months}m"


@dataclass
class NCDData:
    """NCD IPO issuer with all series."""
    company: str
    issuer_id: str
    credit_rating: str
    open_date: str
    close_date: str
    face_value: float
    is_listed: bool
    nri_eligible: bool
    series: List[NCDSeriesData] = field(default_factory=list)

    @property
    def best_yield(self) -> float:
        if not self.series:
            return 0.0
        return max(s.yield_pct for s in self.series)

    @property
    def best_coupon(self) -> float:
        coupon_series = [s for s in self.series if s.coupon_rate > 0]
        if not coupon_series:
            return 0.0
        return max(s.coupon_rate for s in coupon_series)

    @property
    def total_issue_size_cr(self) -> float:
        if self.series:
            # All series share the same issue size, take first
            return self.series[0].issue_size_cr
        return 0.0


def _freq_label(freq: int) -> str:
    """Convert payment frequency number to label."""
    return {
        0: "Cumulative",
        1: "Annual",
        2: "Semi-Annual",
        4: "Quarterly",
        12: "Monthly",
    }.get(freq, str(freq))


def _format_rating(sorted_cr: list, trusted_only: bool = True) -> str:
    """Format sortedCreditRating: [{'CARE': 'A'}, ...] → 'CARE: A'."""
    if not sorted_cr or not isinstance(sorted_cr, list):
        return "N/A"
    parts = []
    for r in sorted_cr:
        if isinstance(r, dict):
            for agency, rating in r.items():
                if trusted_only and agency.strip().upper() not in TRUSTED_AGENCIES:
                    continue
                parts.append(f"{agency}: {rating}")
    return " | ".join(parts) if parts else "N/A"


def _is_trusted_a_series(sorted_cr: list) -> bool:
    """Check if at least one rating is from ICRA/CRISIL/CARE and A-series or above."""
    if not sorted_cr or not isinstance(sorted_cr, list):
        return False
    for r in sorted_cr:
        if not isinstance(r, dict):
            continue
        for agency, rating in r.items():
            if agency.strip().upper() not in TRUSTED_AGENCIES:
                continue
            # Clean rating string
            core = re.sub(r"\s*\((?!CE)[^)]*\)", "", rating).strip()
            rank = _RATING_RANKS.get(core)
            if rank is not None and rank <= MINIMUM_RATING_RANK:
                return True
    return False


def _parse_date(date_str) -> str:
    """Parse ISO date or return as-is."""
    if not date_str:
        return "N/A"
    s = str(date_str)
    if "T" in s:
        s = s.split("T")[0]
    # Convert YYYY-MM-DD to DD-Mon-YYYY for display
    try:
        from datetime import datetime
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return s


def fetch_ncds() -> List[NCDData]:
    """Fetch open NCD IPOs from GoldenPi."""
    if not NCD_IPO_API:
        print("⏭️  NCD IPO skipped — NCD_IPO_API not set in .env")
        return []
    if not NCD_IPO_TOKEN:
        print("⏭️  NCD IPO skipped — NCD_IPO_TOKEN not set in .env")
        return []

    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-gpi-client-token": NCD_IPO_TOKEN,
            "User-Agent": "Mozilla/5.0 (compatible; RPi_market/1.0)",
        }
        resp = requests.post(
            NCD_IPO_API,
            json=DEFAULT_REQUEST_BODY,
            headers=headers,
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()

        # Response: { "data": { "ipoInstDetails": { "IssuerName": { ... }, ... } } }
        ipo_details = payload.get("data", {}).get("ipoInstDetails", {})

        if not ipo_details or not isinstance(ipo_details, dict):
            print("⚠️  NCD IPO API returned no data")
            return []

        ncds = []
        skipped = 0

        for issuer_name, issuer_data in ipo_details.items():
            sorted_cr = issuer_data.get("sortedCreditRating", [])

            # ── Filter: Trusted agency + A-series rating ──
            if not _is_trusted_a_series(sorted_cr):
                skipped += 1
                continue

            company = issuer_data.get("issuerName", issuer_name)
            issuer_id = issuer_data.get("issuerId", "")
            credit_rating = _format_rating(sorted_cr, trusted_only=True)
            close_date = _parse_date(issuer_data.get("ipoCloseDate"))
            face_value = float(issuer_data.get("faceValue", 1000) or 1000)
            is_listed = bool(issuer_data.get("listed", 0))
            nri_eligible = bool(issuer_data.get("nriEligible", 0))

            # Parse series — only keep those with yield >= 10%
            series_list = []
            for inst in issuer_data.get("instDetails", []):
                ytmc = float(inst.get("ytmc", 0) or 0)
                if ytmc < MIN_YIELD_PCT:
                    continue

                coupon = float(inst.get("coupon", 0) or 0)
                tenure_months = int(inst.get("tenureMonth", 0) or 0)
                pip_freq = int(inst.get("pipFreq", 0) or 0)
                fv = float(inst.get("faceValue", face_value) or face_value)
                min_lot = int(inst.get("minLotSize", 1) or 1)
                secured = bool(inst.get("secured", 0))
                issue_size = float(inst.get("issueSize", 0) or 0)
                issue_size_cr = issue_size / 1_00_00_00_000 if issue_size > 0 else 0
                coupon_type = inst.get("couponType", "FIXED") or "FIXED"

                series_list.append(NCDSeriesData(
                    series=inst.get("series", ""),
                    coupon_rate=coupon,
                    yield_pct=ytmc,
                    tenure_months=tenure_months,
                    face_value=fv,
                    interest_freq=_freq_label(pip_freq),
                    min_lot_size=min_lot,
                    secured=secured,
                    issue_size_cr=round(issue_size_cr, 2),
                    coupon_type=coupon_type,
                ))

            # Skip issuer if no series passed the yield filter
            if not series_list:
                skipped += 1
                continue

            series_list.sort(key=lambda s: s.yield_pct, reverse=True)

            ncds.append(NCDData(
                company=company,
                issuer_id=issuer_id,
                credit_rating=credit_rating,
                open_date="",  # not displayed
                close_date=close_date,
                face_value=face_value,
                is_listed=is_listed,
                nri_eligible=nri_eligible,
                series=series_list,
            ))

        ncds.sort(key=lambda n: n.best_yield, reverse=True)
        print(f"📜 NCD IPOs: {len(ncds)} passed filters, {skipped} skipped "
              f"(min yield: {MIN_YIELD_PCT}%, agencies: {', '.join(TRUSTED_AGENCIES)}, rating: A- and above)")
        return ncds

    except Exception as e:
        print(f"❌ NCD IPO fetch error: {e}")
        return []
