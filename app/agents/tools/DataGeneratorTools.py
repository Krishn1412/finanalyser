from typing import Annotated, List, Dict
from langchain_core.tools import tool
import yfinance as yf
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from app.agents.teams.RAGTeam import test_pandas
from app.agents.utils import df_to_base64, get_ticker
from app.db.db_connection import insert_or_update_company_data


_TEMP_DIRECTORY = TemporaryDirectory()
WORKING_DIRECTORY = Path(_TEMP_DIRECTORY.name)


@tool
def fetch_financial_details(
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
        # if not cash_flow_info:
        #     return {"error": "No financial information available."}

        # ans = test_pandas(financial_details_info)
        # print(ans)
        company_data = {
            "cash_flow": df_to_base64(cash_flow_info),
            "balance_sheet": df_to_base64(balance_sheet_info),
            "financials": df_to_base64(financial_details_info),
        }
        company_data_json = json.dumps(company_data, indent=4)
        insert_or_update_company_data(company_name, company_data_json)
        return financial_details_info
    except Exception as e:
        return {"error": f"Failed to fetch data: {repr(e)}"}


if __name__ == "__main__":
    company = "Apple"
    result = fetch_finance_details(company)
    # print(result)
