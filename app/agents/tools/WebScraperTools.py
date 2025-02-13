from typing import Annotated, List
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )
