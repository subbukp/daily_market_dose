import httpx
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
import os

router = APIRouter()

@router.get('/{company_id}')
async def reports(company_id: int):
    try:
        baseurl = os.environ.get("BASE_URL")
        path=os.environ.get("NEWS")
        url = baseurl+path+f"?companyId={company_id}"
        print(url)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return JSONResponse(
            status_code=response.status_code,  
            content=response.json()
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")