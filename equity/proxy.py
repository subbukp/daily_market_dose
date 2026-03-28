import httpx
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
import os
from enum import Enum

class Endpoint(str, Enum):
    latest_news: str="rest/public/getCompanyLatestNews?pageNo=1&pageSize=5&period=1year"
    corporate_news: str="rest/public/getCorporateActionNews?PageNo=1&Pagesize=5"
    pnl_ratio: str="getProfitAndLossReturnRatios?financialDataType=C"
    company_details: str="getCompanyDetailsData?financialDataType=C"
    quaterly_result: str="getQaterlyAndYearlyResults?resultType=Q&financialDataType=C&yearCount=12"
    yearly_result: str="getQaterlyAndYearlyResults?resultType=A&financialDataType=C&yearCount=10"
    balance_sheet: str="getBalanceSheetResults?financialDataType=C&yearCount=10"
    cash_flow: str="getCashFlowResults?financialDataType=C&yearCount=10"
    financial_ratio: str="getFinanceRatiosResults?financialDataType=C&yearCount=10" #ROCE
    shareholders: str="getMajorShareHoldersResults?yearCount=10"
    valuation_ratio: str="getCompanyDetailsDataNew?financialDataType=C"
    related_companies: str="getBusinessHouseAndCompanies?financialDataType=C"
    growth_ratio: str="getFinancialYearReturnRatios?financialDataType=C"  #sales growth, profit growth
    report: str="getCompanyResearchLinks"
    dividend: str="getDividendResults"
    fund_house: str="getFundHousesInvestedInStock"
    about: str="getAboutUsCompanyId"
    last_price: str="getLastClosingPrice"    

proxy_router = APIRouter()

@proxy_router.get('/{path}/{company_id}')
async def reports(company_id: int, path: str):
    try:
        baseurl = os.environ.get("BASE_URL")
        try:
            endpoint=Endpoint[path].value
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid endpoint: {path}")
        separator = "&" if "?" in endpoint else "?"
        url = f"{baseurl}{endpoint}{separator}companyId={company_id}"
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
    
