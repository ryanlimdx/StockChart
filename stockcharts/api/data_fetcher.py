# For fetching data from APIs

import os
import finnhub
import yfinance as yf
import pandas as pd
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, Future

from ..utils import date_utils

try: 
    load_dotenv()
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
except ImportError:
    FINNHUB_API_KEY = None
    ALPHA_VANTAGE_API_KEY = None

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

    def fetch_data_async(self) -> Dict[str, Future]:
        """Submits data fetching tasks to a thread pool."""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                'price': executor.submit(self._get_price_history),
                'macro_news': executor.submit(self._get_macro_news),
                'company_news': executor.submit(self._get_company_news),
                'filings': executor.submit(self._get_sec_filings),
                'insider_transactions': executor.submit(self._get_insider_transactions)
            }
        return futures

    # yfinance
    def _get_price_history(self) -> pd.DataFrame:
        """Fetches the last 3 months of daily stock prices."""
        try:
            stock = yf.Ticker(self.ticker)
            history = stock.history(
                start=date_utils.get_date(self.start_date),
                end=date_utils.get_date(self.end_date)
            )
            return history
        except Exception as e:
            print(f"Error fetching yFinance price history: {e}")
            return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'])
    
    # Alpha Vantage
    def _get_macro_news(self) -> Dict[str, Any]:
        """Fetches macro news."""
        url = (
            f"https://www.alphavantage.co/query?"
            f"function=NEWS_SENTIMENT&"
            f"topics=economy_macro&"
            f"time_from={date_utils.get_date_time(self.start_date)}&"
            f"apikey={ALPHA_VANTAGE_API_KEY}"
        )

        try:
            r = requests.get(url)
            r.raise_for_status() # Raise an exception for bad status codes
            data = r.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Alpha Vantage data: {e}")
            return {}

    # Finnhub
    def _get_company_news(self) -> List[Dict[str, Any]]:
        """Fetches company news."""
        try:
            return self.finnhub_client.company_news(
                self.ticker,
                _from=date_utils.get_date(self.start_date),
                to=date_utils.get_date(self.end_date)
            )
        except Exception as e:
            print(f"Error fetching Finnhub company news: {e}")
            return []
    
    def _get_sec_filings(self) -> List[Dict[str, Any]]:
        """Fetches SEC filings."""
        try: 
            return self.finnhub_client.filings(
                symbol=self.ticker, 
                _from=date_utils.get_date(self.start_date),
                to=date_utils.get_date(self.end_date)
            )
        except Exception as e:
            print(f"Error fetching Finnhub SEC filings: {e}")
            return []
    
    def _get_insider_transactions(self) -> List[Dict[str, Any]]:
        """Fetches insider transactions."""
        try:
            return self.finnhub_client.stock_insider_transactions(
                symbol=self.ticker, 
                _from=date_utils.get_date(self.start_date),
                to=date_utils.get_date(self.end_date)
            )
        except Exception as e:
            print(f"Error fetching Finnhub insider transactions: {e}")
            return []
        
    def test():
        try:
            fetcher = DataFetcher()
            macro_data = fetcher._get_macro_news()
            news_data = fetcher._get_company_news()
            price_data = fetcher._get_price_history()

            if macro_data and 'feed' in macro_data and macro_data['feed']:
                print("\n--- First 5 Macro News Headlines ---")
                for article in macro_data['feed'][:5]:
                    print(f"Headline: {article.get('title', 'No Title')}")
                    print(f"Source: {article.get('source', 'N/A')}")
                    print(f"URL: {article.get('url', 'N/A')}")
                    print("-" * 20)
            else:
                    print("No macro news articles found or an error occurred.")

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

            print("--- Stock Price History ---")
            print("\n--- First 5 Rows ---")
            print(price_data.head())
                
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")