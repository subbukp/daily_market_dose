from fastapi import APIRouter
from equity import urls

router = APIRouter()

router.include_router(urls.router, prefix="/market", tags=["equity"])