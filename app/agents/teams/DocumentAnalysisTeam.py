from langchain_core.messages import HumanMessage
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Sequence, Literal
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
