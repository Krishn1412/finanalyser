from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from config import GOOGLE_API_KEY, TAVILY_API_KEY
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from app.agents.tools.DocumentAnalysisTools import document_retrieval

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
from typing import TypedDict, Sequence, Literal
import pandas as pd
from langchain_core.messages import BaseMessage
from langgraph.managed import IsLastStep
from langgraph.types import Command
from langchain_core.language_models.base import LanguageModelLike
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from app.agents.utils import load_yaml
from langchain_community.tools.tavily_search import TavilySearchResults
from app.agents.tools.RAGTools import q_and_a_utils

tavily_tool = TavilySearchResults(max_results=5, tavily_api_key=TAVILY_API_KEY)


class State(MessagesState):
    next: str


search_agent = create_react_agent(llm, tools=[tavily_tool])


class AgentState(TypedDict):
    """State of the Pandas Agent."""

    messages: Sequence[BaseMessage] 
    is_last_step: IsLastStep 
    df: pd.DataFrame 


document_retreival_agent = create_react_agent(llm, tools=[document_retrieval])


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
        allow_dangerous_code=True
    )
    return pandas_df_agent


q_and_a_util_agent = create_react_agent(llm, tools=[q_and_a_utils])


def document_retreival_node(state: MessagesState) -> Command[Literal["q_and_a_supervisor"]]:
    result = document_retreival_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content, name="vector_search"
                )
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="q_and_a_supervisor",
    )


def yfinance_data_node(state: MessagesState) -> Command[Literal["q_and_a_supervisor"]]:
    human_prompt = state['messages'][0].content
    final_financial_info = q_and_a_util_agent.invoke(state)
    if not isinstance(final_financial_info, pd.DataFrame):
        return Command(
        update={
            "messages": [
                HumanMessage(content="No dataframe found for this company in the db", name="yfinance_db")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="q_and_a_supervisor",
    )
    pandas_df_agent = create_pandas_agent(llm, final_financial_info)

    # get prompt
    prompt_content = load_yaml("../prompts/RAGPrompt.yaml")

    prompt = (
        prompt_content.get("context", "")
        + prompt_content.get("instructions", "")
        + prompt_content.get("examples", "")
    )

    prompt_template = ChatPromptTemplate([("system", prompt), ("user", human_prompt)])
    result = pandas_df_agent.invoke(prompt_template)

    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="yfinance_db")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="q_and_a_supervisor",
    )


def web_search_node(state: State) -> Command[Literal["q_and_a_supervisor"]]:
    result = search_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="web_search")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="q_and_a_supervisor",
    )
