from typing import Annotated, List, Dict
from langchain_core.tools import tool
import yfinance as yf
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from app.Session.RedisSessionManager import SessionManager
from app.agents.utils import collect_and_store_prediction_metrics_yfinance, df_to_base64, get_ticker, merge_dataframes
from app.db.db_connection import (
    insert_or_update_company_data,
    insert_or_update_user_session,
)


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
        if not ticker_data:
            return {"error": "Company not found on Yahoo Finance."}

        # # Create a session to store the data
        # session_manager = SessionManager(
        #     redis_host="localhost", redis_port=6379, session_ttl=3600
        # )
        # session_data = {"company_name": company_name}
        # session_id = session_manager.create_session(session_data)
        # print(f"New session created: {session_id}")

        # # Store session id in the database
        # insert_or_update_user_session(user_id, session_id)

        cash_flow_info = ticker_data.cash_flow
        balance_sheet_info = ticker_data.balance_sheet
        financial_details_info = ticker_data.financials
        
        merge_data = merge_dataframes(cash_flow_info, balance_sheet_info, financial_details_info)
        test = collect_and_store_prediction_metrics_yfinance(company_name, merge_data)

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


