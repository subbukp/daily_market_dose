from fastapi import APIRouter
from .proxy import proxy_router
router = APIRouter()

router.include_router(proxy_router, prefix='/equity', tags=["news"]),
