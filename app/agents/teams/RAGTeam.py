from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from app.agents.utils import db_data_to_df, load_yaml, merge_dataframes
from app.db.db_connection import fetch_company_data
from config import GOOGLE_API_KEY
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
from typing import TypedDict, Sequence, Literal
import pandas as pd
from langgraph.graph.graph import CompiledGraph
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langgraph.managed import IsLastStep
from langgraph.types import Command
from langchain_core.language_models.base import LanguageModelLike
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from app.agents.utils import make_supervisor_node


class AgentState(TypedDict):
    """State of the Pandas Agent."""

    messages: Sequence[BaseMessage]  # Conversation messages
    is_last_step: IsLastStep  # Indicator for the last step
    df: pd.DataFrame  # The DataFrame being operated upon


def create_pandas_agent(llm: LanguageModelLike, dataframe):
    """
    Creates a LangGraph agent for working with pandas DataFrames.
    """
    pandas_df_agent = create_pandas_dataframe_agent(
        llm,
        dataframe,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True,
    )
    return pandas_df_agent


def test_pandas(df):
    pandas_df_agent = create_pandas_agent(llm, df)
    return pandas_df_agent.invoke(
        "what is the Cost of Revenue for the latest year? This might be the index of the dataframe."
    )


def q_and_a_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    human_prompt = state['messages'][0].content

    # company_name = company_name_message.content
    data = fetch_company_data(company_name)
    cash_flow, balance_sheet, financials = db_data_to_df(data)
    final_financial_info = merge_dataframes(cash_flow, balance_sheet, financials)
    pandas_df_agent = create_pandas_agent(llm, final_financial_info)

    # get prompt
    prompt_content = load_yaml("../prompts/RAGPrompt.yaml")

    prompt = (
        prompt_content.get("context", "")
        + prompt_content.get("instructions", "")
        + prompt_content.get("examples", "")
    )

    prompt_template = ChatPromptTemplate([("system", prompt), ("user", human_question)])
    result = pandas_df_agent.invoke(prompt_template)

    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="q_and_a")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

