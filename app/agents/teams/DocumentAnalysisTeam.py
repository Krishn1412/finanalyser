from app.agents.tools.DocumentAnalysisTools import document_ingestion, document_retrieval
from config import GOOGLE_API_KEY
import os
from pathlib import Path
import google.generativeai as genai
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType
from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from config import GOOGLE_API_KEY
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Sequence, Literal
import pandas as pd
from langchain_core.messages import BaseMessage
from langgraph.managed import IsLastStep
from langgraph.types import Command
from langchain_core.language_models.base import LanguageModelLike
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from app.agents.utils import load_yaml, make_supervisor_node

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)


document_ingestion_agent = create_react_agent(llm, tools=[document_ingestion])

document_retreival_agent = create_react_agent(llm, tools=[document_retrieval])

def document_ingestion_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = document_ingestion_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content, name="fetch_financial_data"
                )
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

def document_retreival_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = document_retreival_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content, name="fetch_financial_data"
                )
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )

