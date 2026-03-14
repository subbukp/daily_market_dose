"""
Data Sources — Each module fetches from one API.

Add a new data source by:
1. Create a new file in data/sources/
2. Define a dataclass for the data model
3. Define a fetch_*() function
4. Add the API env var to config/settings.py
5. Wire it into data/fetcher.py → fetch_all_data()
6. Add formatting in data/formatter.py
"""

from data.sources.mmi import MMIData, fetch_mmi
from data.sources.quotes import QuoteData, fetch_quotes
from data.sources.ipo import IPOData, fetch_ipos
from data.sources.ncd import NCDData, fetch_ncds
from data.sources.secondary_bonds import BondData, fetch_secondary_bonds
from data.sources.precious_metals import PreciousMetalsSnapshot, fetch_precious_metals
from data.sources.us_fear_greed import USFearGreedData, fetch_us_fear_greed

__all__ = [
    "MMIData", "fetch_mmi",
    "QuoteData", "fetch_quotes",
    "IPOData", "fetch_ipos",
    "NCDData", "fetch_ncds",
    "BondData", "fetch_secondary_bonds",
    "PreciousMetalsSnapshot", "fetch_precious_metals",
    "USFearGreedData", "fetch_us_fear_greed",
]

