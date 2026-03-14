"""
Data Fetcher — Orchestrator that calls all modular data sources.

Each source lives in data/sources/<name>.py and is self-contained.
This file just wires them together into a single fetch_all_data() call.
"""

import sys
import os
from datetime import datetime
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import WATCHLIST

# Import all data sources
from data.sources.mmi import MMIData, fetch_mmi
from data.sources.quotes import QuoteData, fetch_quotes
from data.sources.ipo import IPOData, fetch_ipos
from data.sources.ncd import NCDData, fetch_ncds
from data.sources.secondary_bonds import BondData, fetch_secondary_bonds
from data.sources.precious_metals import PreciousMetalsSnapshot, fetch_precious_metals
from data.sources.us_fear_greed import USFearGreedData, fetch_us_fear_greed


def fetch_all_data() -> Dict:
    """Master fetch — calls all configured data sources."""
    all_sids = [item["sid"] for item in WATCHLIST]

    if not all_sids:
        print("⚠️  No tickers configured. Set TICKERS in .env")

    return {
        "mmi": fetch_mmi(),
        "us_fg": fetch_us_fear_greed(),
        "quotes": fetch_quotes(all_sids),
        "metals": fetch_precious_metals(),
        "ipos": fetch_ipos(),
        "ncds": fetch_ncds(),
        "bonds": fetch_secondary_bonds(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
