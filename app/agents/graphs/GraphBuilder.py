from typing import Annotated, Literal, Sequence, TypedDict
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from app.agents.teams.DataGeneratorTeam import document_ingestion_node, fetch_financial_data_node
from pathlib import Path
from app.agents.teams.RAGTeam import document_retreival_node, yfinance_data_node, web_search_node
from app.agents.utils import load_yaml, make_supervisor_node
from config import GOOGLE_API_KEY
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
PDF_STORAGE_DIR = Path(__file__).parent.parent.parent.parent / "storage" / "pdfs"

# Ensure PDF storage directory exists
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
pdf_filename = PDF_STORAGE_DIR / "1.pdf"


class State(MessagesState):
    next: str


class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Create data fetch and store graph
prompt_content = load_yaml("app/agents/prompts/Supervisor.yaml")
data_fetch_and_store_supervisor_node = make_supervisor_node(
    llm, ["fetch_financial_data", "data_ingestion"], prompt_content
)

data_fetch_and_store_builder = StateGraph(MessagesState)
data_fetch_and_store_builder.add_node("data_fetch_and_store_supervisor", data_fetch_and_store_supervisor_node)
data_fetch_and_store_builder.add_node("fetch_financial_data", fetch_financial_data_node)
data_fetch_and_store_builder.add_node("data_ingestion", document_ingestion_node)
data_fetch_and_store_builder.add_edge(START, "data_fetch_and_store_supervisor")

data_fetch_and_store_graph = data_fetch_and_store_builder.compile()


# Q/A graph builder:
prompt_content = load_yaml("app/agents/prompts/QnAPrompt.yaml")
q_and_a_supervisor_node = make_supervisor_node(
    llm, ["data_retrieval", "yfinance_data", "web_search_node"], prompt_content
)
q_and_a_builder = StateGraph(AgentState)
q_and_a_builder.add_node("q_and_a_supervisor", q_and_a_supervisor_node)
q_and_a_builder.add_node("data_retrieval", document_retreival_node)
q_and_a_builder.add_node("yfinance_data", yfinance_data_node)
q_and_a_builder.add_node("web_search_node", web_search_node)
q_and_a_builder.add_edge(START, "q_and_a_supervisor")

# Compile
q_and_a_graph = q_and_a_builder.compile()


# Finalyser graph
prompt_content = load_yaml("app/agents/prompts/Supervisor.yaml")
finalyser_node = make_supervisor_node(
    llm, ["data_fetch_and_store_team", "q_and_a_team"], prompt_content
)


def call_data_fetch_and_store_team(state: State) -> Command[Literal["finalyser_supervisor"]]:
    response = data_fetch_and_store_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response["messages"][-1].content, name="research_team"
                )
            ]
        },
        goto="finalyser_supervisor",
    )


def call_q_and_a_team(state: State) -> Command[Literal["finalyser_supervisor"]]:
    response = q_and_a_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response["messages"][-1].content, name="writing_team"
                )
            ]
        },
        goto="finalyser_supervisor",
    )


# Define the graph.
finalyser_builder = StateGraph(State)
finalyser_builder.add_node("finalyser_supervisor", finalyser_node)
finalyser_builder.add_node("data_fetch_and_store_team", call_data_fetch_and_store_team)
finalyser_builder.add_node("q_and_a_team", call_q_and_a_team)
finalyser_builder.add_edge(START, "finalyser_supervisor")


finalyser_graph = finalyser_builder.compile()



# image_bytes = finalyser_graph.get_graph().draw_mermaid_png()


# with open("output_image.png", "wb") as f:
#     f.write(image_bytes)

# import os

# os.system("open output_image.png")


