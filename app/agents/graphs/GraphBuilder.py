from typing import List, Optional, Literal
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from app.agents.teams.DataGeneratorTeam import fetch_financial_data_node
from app.agents.teams.RAGTeam import q_and_a_node
from app.agents.tools.DataGeneratorTools import fetch_financial_details
from app.agents.utils import make_supervisor_node
from config import GOOGLE_API_KEY
from IPython.display import Image, display
import os

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)


# Create data generator graph
finalyser_supervisor_node = make_supervisor_node(llm, ["fetch_financial_data", "q_and_a"])

finalyser_builder = StateGraph(MessagesState)
finalyser_builder.add_node("supervisor", finalyser_supervisor_node)
finalyser_builder.add_node("fetch_financial_data", fetch_financial_data_node)
finalyser_builder.add_node("q_and_a", q_and_a_node)

finalyser_builder.add_edge(START, "supervisor")
finalyser_graph = finalyser_builder.compile()


# # display(Image(finalyser_graph.get_graph().draw_mermaid_png()))
# image_bytes = finalyser_graph.get_graph().draw_mermaid_png()


# with open("output_image.png", "wb") as f:
#     f.write(image_bytes)

# import os
# os.system("open output_image.png")

for s in finalyser_graph.stream(
    {
        "messages": [
            ("user", "What is the net revenue for APPLE this financial year?")
        ],
    },
    {"recursion_limit": 150},
):
    print(s)
    print("---")

# s = finalyser_graph.stream(
#     {
#         "messages": [
#             ("user", "fetch the finanical data for apple")
#         ],
#     }
# )
# print(s)