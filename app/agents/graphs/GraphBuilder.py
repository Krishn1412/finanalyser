from typing import Annotated, List, Optional, Literal, Sequence, TypedDict
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from app.agents.teams.DataGeneratorTeam import fetch_financial_data_node
from app.agents.teams.DocumentAnalysisTeam import (
    document_ingestion_node,
    document_retreival_node,
)
from pathlib import Path
import asyncio
import PIL.Image
from app.agents.teams.RAGTeam import q_and_a_node
from app.agents.teams.WebScraperTeam import search_node, web_scraper_node
from app.agents.tools.DataGeneratorTools import fetch_financial_details
from app.agents.utils import make_supervisor_node
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


# retriever_tool = DocumentRetriever.get_retriever(pdf_filename)
class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Create data generator graph
# finalyser_supervisor_node = make_supervisor_node(
#     llm, ["fetch_financial_data", "q_and_a"]
# )

# finalyser_builder = StateGraph(MessagesState)
# finalyser_builder.add_node("supervisor", finalyser_supervisor_node)
# finalyser_builder.add_node("fetch_financial_data", fetch_financial_data_node)
# finalyser_builder.add_node("q_and_a", q_and_a_node)

# finalyser_builder.add_edge(START, "supervisor")
# finalyser_graph = finalyser_builder.compile()


# Document Anlysis graph builder:
# pdf_filename = PDF_STORAGE_DIR / "1.pdf"
# retriever_tool = call_document_analysis(pdf_filename)

# workflow = StateGraph(AgentState)

# # Define the nodes we will cycle between
# data_ingestion_supervisor_node = make_supervisor_node(
#     llm, ["data_ingestion", "data_retrieval"]
# )
# workflow.add_node("supervisor", data_ingestion_supervisor_node)
# workflow.add_node("data_ingestion", document_ingestion_node)
# workflow.add_node("data_retrieval", document_retreival_node)

# # Call agent node to decide to retrieve or not
# workflow.add_edge(START, "supervisor")

# # Compile
# graph = workflow.compile()


# Web Scraper graph builder

webscraper_supervisor_node = make_supervisor_node(llm, ["search", "web_scraper"])

webscraper_builder = StateGraph(MessagesState)
webscraper_builder.add_node("supervisor", webscraper_supervisor_node)
webscraper_builder.add_node("search", search_node)
webscraper_builder.add_node("web_scraper", web_scraper_node)

webscraper_builder.add_edge(START, "supervisor")
webscraper_graph = webscraper_builder.compile()

# from IPython.display import Image, display

# # try:
# #     display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
# # except Exception:
# #     # This requires some extra dependencies and is optional
# #     pass

# # # display(Image(finalyser_graph.get_graph().draw_mermaid_png()))
# image_bytes = webscraper_graph.get_graph().draw_mermaid_png()


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
for output in webscraper_graph.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")

# f"Ingest the document present at {pdf_filename}"
# "What is the profit before tax for 2021?"
