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
from app.agents.utils import DocumentRetriever, load_yaml, make_supervisor_node

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

MODEL = "gemini-1.5-pro"


def create_gemini_agent():
    model = genai.GenerativeModel(MODEL)
    return model


gemini_agent = create_gemini_agent()
PDF_STORAGE_DIR = Path(__file__).parent.parent.parent.parent / "storage" / "pdfs"

# Ensure PDF storage directory exists
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
pdf_filename = PDF_STORAGE_DIR / "1.pdf"

retriever_tool = DocumentRetriever.get_retriever(pdf_filename)

def agent_node(state: MessagesState):
    """
    Invokes the agent model to generate a response based on the current state.
    """
    print("---CALL AGENT---")
    messages = state["messages"]

    llm = ChatVertexAI(model="gemini-pro")
    llm_with_tools = llm.bind_tools(retriever_tool)
    response = llm_with_tools.invoke(messages)
    return Command(
        update={
            "messages": [HumanMessage(content=response.text, name="agent_response")]
        }
    )


def rewrite_query_node(state: MessagesState):
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
        }
    )


def generate_answer_node(state: MessagesState):
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
        }
    )


import google.generativeai as genai
from typing import Literal
from pydantic import BaseModel, Field



def grade_documents(state) -> Literal["generate", "rewrite"]:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (messages): The current state

    Returns:
        str: A decision for whether the documents are relevant or not
    """

    print("---CHECK RELEVANCE---")

    # Data model for response validation
    class Grade(BaseModel):
        """Binary score for relevance check."""
        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    # LLM Model
    model = genai.GenerativeModel("gemini-pro")  # Use Gemini-Pro model

    # Extract messages
    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    print("question:", question)
    print("context:", docs)

    # Prompt
    prompt = f"""You are a grader assessing the relevance of a retrieved document to a user question.

    Here is the retrieved document:
    {docs}

    Here is the user question:
    {question}

    If the document contains keyword(s) related to the question, grade it as relevant.
    Respond with a binary score: 'yes' if relevant, 'no' otherwise.
    """

    # Get response from Gemini
    response = model.generate_content(prompt)

    # Extracting the score (Ensure it's clean)
    score = response.text.strip().lower()

    if score.startswith("yes"):
        print("---DECISION: DOCS RELEVANT---")
        return "generate"

    else:
        print("---DECISION: DOCS NOT RELEVANT---")
        print(score)
        return "rewrite"
