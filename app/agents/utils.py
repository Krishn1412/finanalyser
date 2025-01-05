import requests
import pickle
import base64


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
    base64_bytes = base64.b64encode(pickle_bytes).decode(
        "utf-8"
    )
    return base64_bytes

def db_data_to_df(company_data):
    cash_flow_info = pickle.loads(base64.b64decode(company_data["cash_flow"]))
    balance_sheet_info = pickle.loads(base64.b64decode(company_data["balance_sheet"]))
    financial_details_info = pickle.loads(base64.b64decode(company_data["financials"]))

    return cash_flow_info, balance_sheet_info, financial_details_info
