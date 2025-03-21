from typing import List, Optional, Literal
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from app.agents.tools.DataGeneratorTools import fetch_financial_details
from app.agents.tools.DocumentAnalysisTools import document_ingestion
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)


fetch_financial_details_agent = create_react_agent(llm, tools=[fetch_financial_details])
document_ingestion_agent = create_react_agent(llm, tools=[document_ingestion])


def fetch_financial_data_node(state: MessagesState) -> Command[Literal["data_fetch_and_store_supervisor"]]:
    result = fetch_financial_details_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content, name="fetch_financial_data"
                )
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="data_fetch_and_store_supervisor",
    )


def document_ingestion_node(state: MessagesState) -> Command[Literal["data_fetch_and_store_supervisor"]]:
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
        goto="data_fetch_and_store_supervisor",
    )
