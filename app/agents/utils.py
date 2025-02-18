import requests
import pickle
import base64
from typing import List, Optional, Literal, TypedDict, Tuple
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field
import pandas as pd
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
import yaml
from langchain_core.prompts import ChatPromptTemplate


def make_supervisor_node(llm: BaseChatModel, members: list[str], prompt_content) -> str:
    options = ["FINISH"] + members

    system_prompt = (
        prompt_content.get("context", "")
        + prompt_content.get("instructions", "")
        + str(prompt_content.get("examples", ""))
    )

    # class Router(TypedDict):
    #     """Worker to route to next. If no workers needed, route to FINISH."""

    #     next: Literal[*options]

    class Router(BaseModel):
        """Route to the next role one of """ + ", ".join(options)

        worker: Literal[tuple(options)] = Field(
            ...,
            description="Next worker, one of " + ", ".join(options),
        )

    def supervisor_node(state: MessagesState) -> Command[Literal[*members, "__end__"]]:
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response.worker
        if goto == "FINISH":
            goto = END

        return Command(goto=goto)

    return supervisor_node


def get_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance, params=params, headers={"User-Agent": user_agent})
    data = res.json()

    company_code = data["quotes"][0]["symbol"]
    return company_code


def df_to_base64(df):
    pickle_bytes = pickle.dumps(df)
    base64_bytes = base64.b64encode(pickle_bytes).decode("utf-8")
    return base64_bytes


def db_data_to_df(company_data):
    cash_flow_info = pickle.loads(base64.b64decode(company_data["cash_flow"]))
    balance_sheet_info = pickle.loads(base64.b64decode(company_data["balance_sheet"]))
    financial_details_info = pickle.loads(base64.b64decode(company_data["financials"]))

    return cash_flow_info, balance_sheet_info, financial_details_info


def merge_dataframes(df1, df2, df3):
    common_columns = df1.columns.intersection(df2.columns).intersection(df3.columns)

    df1 = df1[common_columns]
    df2 = df2[common_columns]
    df3 = df3[common_columns]

    concatenated_df = pd.concat([df1, df2, df3])

    concatenated_df = concatenated_df[~concatenated_df.index.duplicated(keep="first")]

    return concatenated_df


def load_yaml(file_path: str):
    """Load a YAML file and return its content."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def collect_and_store_prediction_metrics_yfinance(comapny_name, df_yf):
    df = df_yf
    df_metrics = pd.DataFrame({
    "revenue": [df.loc["Total Revenue"].values] if "Total Revenue" in df.index else [None],
    "net_income": [df.loc["Net Income"][0]] if "Net Income" in df.index else [None],
    "current_assets": [df.loc["Total Assets"][0]] if "Total Assets" in df.index else [None],
    "current_liabilities": [df.loc["Total Liabilities Net Minority Interest"][0]] if "Total Liabilities Net Minority Interest" in df.index else [None],
    "total_debt": [df.loc["Total Debt"][0]] if "Total Debt" in df.index else [None],
    "total_equity": [df.loc["Total Equity Gross Minority Interest"][0]] if "Total Equity Gross Minority Interest" in df.index else [None],
    "operating_cash_flow": [df.loc["Operating Cash Flow"][0]] if "Operating Cash Flow" in df.index else [None],
    "capital_expenditures": [df.loc["Capital Expenditure"][0]] if "Capital Expenditure" in df.index else [None]
})

    # Compute financial metrics
    df_metrics["revenue_growth"] = df_metrics["revenue"].pct_change() * 100  # % Revenue Growth
    df_metrics["net_profit_margin"] = (df_metrics["net_income"] / df_metrics["revenue"].values[0]) * 100  # % Net Profit Margin
    df_metrics["current_ratio"] = df_metrics["current_assets"] / df_metrics["current_liabilities"]  # Current Ratio
    df_metrics["debt_to_equity"] = df_metrics["total_debt"] / df_metrics["total_equity"]  # Debt-to-Equity Ratio
    df_metrics["free_cash_flow"] = df_metrics["operating_cash_flow"] - df_metrics["capital_expenditures"]  # Free Cash Flow
    df_metrics["return_on_equity"] = (df_metrics["net_income"] / df_metrics["total_equity"]) * 100  # % ROE

    # Select relevant columns
    df_metrics = df[["revenue_growth", "net_profit_margin", "current_ratio", "debt_to_equity",
                      "free_cash_flow", "return_on_equity"]].dropna()

    return df_metrics


