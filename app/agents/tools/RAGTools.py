from typing import Annotated, Dict
from app.Session.RedisSessionManager import SessionManager
from app.agents.utils import db_data_to_df, merge_dataframes
from app.db.db_connection import fetch_company_data, fetch_session_id
from langchain_core.tools import tool


@tool
def q_and_a_utils(
    company_name: Annotated[
        str, "The company name that user wants to know about"
    ]
) -> Annotated[str, "financial info"]:
    """Fetch financial details for a given company, and return it"""
   
    data = fetch_company_data(company_name)
    cash_flow, balance_sheet, financials = db_data_to_df(data)
    final_financial_info = merge_dataframes(cash_flow, balance_sheet, financials)
    return final_financial_info
