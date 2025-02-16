from typing import Annotated, List, Optional, Literal, Sequence, TypedDict
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from app.agents.teams.DataGeneratorTeam import fetch_financial_data_node
from pathlib import Path
import asyncio
import PIL.Image
from app.agents.teams.RAGTeam import document_retreival_node, yfinance_data_node, web_search_node
from app.agents.teams.WebScraperTeam import search_node, web_scraper_node
from app.agents.tools.DataGeneratorTools import fetch_financial_details
from app.agents.utils import load_yaml, make_supervisor_node
from config import GOOGLE_API_KEY
from IPython.display import Image, display
import os
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage, SystemMessage

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


# # Create data fetch and store graph
# prompt_content = load_yaml("app/agents/prompts/Supervisor.yaml")
# data_fetch_and_store_supervisor_node = make_supervisor_node(
#     llm, ["fetch_financial_data", "data_ingestion"], prompt_content
# )

# data_fetch_and_store_builder = StateGraph(MessagesState)
# data_fetch_and_store_builder.add_node("data_fetch_and_store_supervisor", data_fetch_and_store_supervisor_node)
# data_fetch_and_store_builder.add_node("fetch_financial_data", fetch_financial_data_node)
# data_fetch_and_store_builder.add_node("data_ingestion", document_ingestion_node)
# data_fetch_and_store_builder.add_edge(START, "data_fetch_and_store_supervisor")

# data_generator_graph = data_fetch_and_store_builder.compile()


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


# # Web Scraper graph builder
# prompt_content = load_yaml("app/agents/prompts/Supervisor.yaml")
# webscraper_supervisor_node = make_supervisor_node(llm, ["search", "web_scraper"], prompt_content)

# webscraper_builder = StateGraph(MessagesState)
# webscraper_builder.add_node("webscraper_supervisor", webscraper_supervisor_node)
# webscraper_builder.add_node("search", search_node)
# webscraper_builder.add_node("web_scraper", web_scraper_node)
# webscraper_builder.add_edge(START, "webscraper_supervisor")

# webscraper_graph = webscraper_builder.compile()


# # Finalyser graph
# prompt_content = load_yaml("app/agents/prompts/Supervisor.yaml")
# finalyser_node = make_supervisor_node(
#     llm, ["data_fetching_team", "document_analysis_team", "web_search_team"], prompt_content
# )


# def call_data_fetching_team(state: State) -> Command[Literal["supervisor"]]:
#     response = data_generator_graph.invoke({"messages": state["messages"][-1]})
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response["messages"][-1].content, name="research_team"
#                 )
#             ]
#         },
#         goto="supervisor",
#     )


# def call_document_analysis_team(state: State) -> Command[Literal["supervisor"]]:
#     response = document_analysis_graph.invoke({"messages": state["messages"][-1]})
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response["messages"][-1].content, name="writing_team"
#                 )
#             ]
#         },
#         goto="supervisor",
#     )


# def call_web_search_team(state: State) -> Command[Literal["supervisor"]]:
#     response = webscraper_graph.invoke({"messages": state["messages"][-1]})
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response["messages"][-1].content, name="writing_team"
#                 )
#             ]
#         },
#         goto="supervisor",
#     )


# # Define the graph.
# finalyser_builder = StateGraph(State)
# finalyser_builder.add_node("supervisor", finalyser_node)
# finalyser_builder.add_node("data_fetching_team", call_data_fetching_team)
# finalyser_builder.add_node("document_analysis_team", call_document_analysis_team)
# finalyser_builder.add_node("web_search_team", call_web_search_team)
# finalyser_builder.add_edge(START, "supervisor")


# finalyser_graph = finalyser_builder.compile()
# from IPython.display import Image, display

# # try:
# #     display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
# # except Exception:
# #     # This requires some extra dependencies and is optional
# #     pass

# # # display(Image(finalyser_graph.get_graph().draw_mermaid_png()))
# image_bytes = q_and_a_graph.get_graph().draw_mermaid_png()


# with open("output_image.png", "wb") as f:
#     f.write(image_bytes)

# import os

# os.system("open output_image.png")

# for s in finalyser_graph.stream(
#     {
#         "messages": [
#             (
#                 "user",
#                 "Answer me the question, what is the net revenue of Amazon, user_id is anon_11",
#             )
#         ],
#     },
#     {"recursion_limit": 150},
# ):
#     print(s)
#     print("---")

# s = graph.stream(
#     {
#         "messages": [
#             ("user", "What is the profit before tax for 2021?")
#         ],
#     }
# )
# print(s)
# Answer me the question, what is the net revenue of Amazon, user_id is anon_11
# Fetch the financial data of Amazon, user_id is anon_11
import pprint

inputs = {
    "messages": [
        ("user", "when is Taylor Swift's next tour?"),
    ]
}
for output in q_and_a_graph.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")

# f"Ingest the document present at {pdf_filename}"
# "What is the profit before tax for 2021?"
