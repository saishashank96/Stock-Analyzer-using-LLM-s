import json
from urllib.request import urlopen
from urllib.parse import quote
from langchain_core.tools import tool


def fetch_live_price_yahoo(ticker: str) -> float | None:
    """Fetch live NSE price from Yahoo Finance for a ticker like RELIANCE.NS.

    Returns a float price in INR, or None if unavailable.
    """
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={quote(ticker)}"
        with urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        result = data.get("quoteResponse", {}).get("result", [])
        if not result:
            return None
        price = result[0].get("regularMarketPrice")
        return float(price) if price is not None else None
    except Exception:
        return None


@tool("get_price_yahoo")
def get_price_yahoo(ticker: str) -> float:
    """Return live price in INR for an NSE ticker (e.g., RELIANCE.NS). Raises on failure."""
    price = fetch_live_price_yahoo(ticker)
    if price is None:
        raise ValueError(f"Price unavailable for {ticker}")
    return price


