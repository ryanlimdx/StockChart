# For fetching data from APIs

import os
import finnhub
from utils import date_utils
from dotenv import load_dotenv
from typing import Dict, Any, List

try: 
    load_dotenv()
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
except ImportError:
    FINNHUB_API_KEY = None

class DataFetcher:
    """Handles data fetching from APIs"""
    def __init__(self, ticker: str = "NVDA"):
        if not FINNHUB_API_KEY:
            raise ValueError("Finnhub API key not found in .env")
        
        self.ticker = ticker
        self.end_date = date_utils.now()
        self.start_date = date_utils.backdate(past_days_ago=90)

        # APIs
        self.finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

    def get_company_news(self) -> List[Dict[str, Any]]:
        """Fetches company news within the date range."""
        return self.finnhub_client.company_news(
            self.ticker,
            _from=self.start_date,
            to=self.end_date
        )

# Test
try:
    fetcher = DataFetcher()
    news_data = fetcher.get_company_news()

    print(f"Fetched {len(news_data)} news articles.")
    if news_data:
        print("\n--- First 3 News Articles ---")
        for article in news_data[:3]:
            print(f"Headline: {article.get('headline', 'N/A')}")
            print(f"Source: {article.get('source', 'N/A')}")
            print(f"URL: {article.get('url', 'N/A')}")
            print("-" * 20)
    else:
        print("No news articles found.")
        
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")