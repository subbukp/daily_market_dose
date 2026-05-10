from fastapi import APIRouter
from .proxy import proxy_router
from .ticker import ticker_router
router = APIRouter()

router.include_router(proxy_router, prefix='/equity', tags=["equity_endpoints"]),
router.include_router(ticker_router, prefix='/searchString', tags=["ticker"]),
