from typing import Annotated, List, Dict
from langchain_core.tools import tool 
import yfinance as yf
from pathlib import Path
from tempfile import TemporaryDirectory

from app.agents.utils import get_ticker



_TEMP_DIRECTORY = TemporaryDirectory()
WORKING_DIRECTORY = Path(_TEMP_DIRECTORY.name)

@tool
def fetch_finance_details(
    company_name: Annotated[str, "Name of the company to fetch finance details for."]
) -> Annotated[Dict[str, str], "Dictionary of finance details."]:
    """Fetch financial details of a given company using yfinance."""
    try:
        # Search for the company's ticker symbol
        ticker_symbol = get_ticker(company_name)
        ticker_data = yf.Ticker(ticker_symbol)
        print(company_name)
        print(ticker_data)
        if not ticker_data:
            return {"error": "Company not found on Yahoo Finance."}
            
        cash_flow_info = ticker_data.cash_flow
        balance_sheet_info = ticker_data.balance_sheet
        financial_details_info = ticker_data.financials
        if not cash_flow_info:
            return {"error": "No financial information available."}
        
        financial_details = {
            "Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Market Cap": str(info.get("marketCap", "N/A")),
            "Price to Earnings (P/E)": str(info.get("trailingPE", "N/A")),
            "Dividend Yield": str(info.get("dividendYield", "N/A")),
            "Revenue": str(info.get("totalRevenue", "N/A")),
            "Net Income": str(info.get("netIncomeToCommon", "N/A")),
        }

        return financial_details
    except Exception as e:
        return {"error": f"Failed to fetch data: {repr(e)}"}


if __name__ == "__main__":
    company = "Apple"  
    result = fetch_finance_details(company)
    # print(result)
