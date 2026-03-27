from fastapi import APIRouter
from .others import report_router
router = APIRouter()

router.include_router(report_router, prefix='/reports', tags=["news"])