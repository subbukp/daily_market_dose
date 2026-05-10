from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

ticker_router = APIRouter()

@ticker_router.get("/{searchString}")
async def ticker(searchString: str):
    baseurl = os.environ.get("BASE_URL")
    url = f"{baseurl}globalSearch?searchString={searchString}"
    try:
        company_map = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            companies = response.json().get("companyList", [])
            for company in companies:
                company_map[company.get("name", "")] = company.get("id","")
            return JSONResponse(
                status_code=response.status_code,
                content=company_map
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")