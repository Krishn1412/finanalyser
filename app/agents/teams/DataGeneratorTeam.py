from typing import List, Optional, Literal
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from app.agents.tools.DataGeneratorTools import fetch_financial_details
from app.agents.utils import make_supervisor_node
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)


fetch_financial_details_agent = create_react_agent(llm, tools=[fetch_financial_details])


def fetch_financial_data_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = fetch_financial_details_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="web_scraper")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


research_supervisor_node = make_supervisor_node(llm, ["fetch financial data"])

research_builder = StateGraph(MessagesState)
research_builder.add_node("fetch financial data", fetch_financial_data_node)

research_builder.add_edge(START, "supervisor")
research_graph = research_builder.compile()
