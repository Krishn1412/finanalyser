from typing import Annotated, Dict
from app.Session.RedisSessionManager import SessionManager
from app.agents.utils import db_data_to_df, merge_dataframes
from app.db.db_connection import fetch_company_data, fetch_session_id
from langchain_core.tools import tool


@tool
def q_and_a_utils(
    human_prompt: Annotated[
        str, "The question that human is asking apart from the user ID"
    ],
    user_id: Annotated[str, "User ID for the use currently using the agent."],
) -> Annotated[str, str, "financial info and the human prompt"]:
    """Fetch financial details for a given user and its present session company, and return it along with parsed human prompt"""
    session_id = fetch_session_id(user_id)

    session_manager = SessionManager(
        redis_host="localhost", redis_port=6379, session_ttl=3600
    )
    session_data = session_manager.get_session(session_id)
    company_name = session_data["company_name"]

    data = fetch_company_data(company_name)
    cash_flow, balance_sheet, financials = db_data_to_df(data)
    final_financial_info = merge_dataframes(cash_flow, balance_sheet, financials)
    return final_financial_info, human_prompt
