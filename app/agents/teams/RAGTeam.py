from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from app.agents.utils import db_data_to_df
from app.db.db_connection import fetch_company_data
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
from typing import TypedDict, Sequence
import pandas as pd
from langgraph.graph.graph import CompiledGraph
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langgraph.managed import IsLastStep
from langgraph.types import Command
from langchain_core.language_models.base import LanguageModelLike
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langgraph.checkpoint.memory import MemorySaver


class AgentState(TypedDict):
    """State of the Pandas Agent."""

    messages: Sequence[BaseMessage]  # Conversation messages
    is_last_step: IsLastStep  # Indicator for the last step
    df: pd.DataFrame  # The DataFrame being operated upon


def create_pandas_agent(llm: LanguageModelLike, input):
    """
    Creates a LangGraph agent for working with pandas DataFrames.
    """
    company_name = input["name"]
    data = fetch_company_data(company_name)
    cash_flow, balance_sheet, financials = db_data_to_df(data)


def test_pandas(df):
    pandas_df_agent = create_pandas_agent(llm, df)
    return pandas_df_agent.invoke(
        "what is the Cost of Revenue for the latest year? This might be the index of the dataframe."
    )
