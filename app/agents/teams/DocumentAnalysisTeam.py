from config import GOOGLE_API_KEY
import os
import google.generativeai as genai
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType
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
# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

MODEL = "gemini-1.5-pro"


def create_gemini_agent():
    model = genai.GenerativeModel(MODEL)
    return model


gemini_agent = create_gemini_agent()


def agent_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    """
    Invokes the agent model to generate a response based on the current state.
    """
    print("---CALL AGENT---")
    messages = state["messages"]

    response = gemini_agent.generate_content(messages, stream=False)

    return Command(
        update={
            "messages": [HumanMessage(content=response.text, name="agent_response")]
        },
        goto="supervisor",
    )


def rewrite_query_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    """
    Transforms the query to produce a better question.
    """
    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content

    prompt = f"""
    Look at the input and try to reason about the underlying semantic intent/meaning.
    Here is the initial question:
    -------
    {question}
    -------
    Reformulate an improved question:
    """

    response = gemini_agent.generate_content([prompt], stream=False)

    return Command(
        update={
            "messages": [HumanMessage(content=response.text, name="rewritten_query")]
        },
        goto="supervisor",
    )


def generate_answer_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    """
    Generates an answer using retrieved context.
    """
    print("---GENERATE ANSWER---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]

    docs = last_message.content

    # Formatting the context
    formatted_context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
    Use the provided context to generate an insightful answer.

    Context:
    {formatted_context}

    Question:
    {question}

    Answer:
    """

    response = gemini_agent.generate_content([prompt], stream=False)

    return Command(
        update={
            "messages": [HumanMessage(content=response.text, name="generated_answer")]
        },
        goto="supervisor",
    )
