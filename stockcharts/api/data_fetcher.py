# For fetching data from APIs

import os
import finnhub
import yfinance as yf
import pandas as pd
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from stockcharts.utils import date_utils

try: 
    load_dotenv()
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
except ImportError:
    FINNHUB_API_KEY = None
    ALPHA_VANTAGE_API_KEY = None

class DataFetcher:
    """Handles data fetching from APIs"""
    def __init__(self, ticker: str = "NVDA", range: int = 90):
        if not FINNHUB_API_KEY:
            raise ValueError("Finnhub API key not found in .env")
        
        self.ticker = ticker
        self.end_date = date_utils.now()
        self.start_date = date_utils.backdate(past_days_ago=range)

        # APIs
        self.finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    
    def fetch_price_async(self) -> Future:
        """Submits the price fetching task to a thread pool."""
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(self._get_price_history)

    def fetch_events_async(self) -> Dict[str, Future]:
        """Submits all event fetching tasks to a thread pool."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'macro_news': executor.submit(self._get_macro_news),
                'company_news': executor.submit(
                    self._fetch_all_from_finnhub_endpoint,
                    self.finnhub_client.company_news,
                    symbol=self.ticker,
                    batch_size=5
                ),
                'filings': executor.submit(
                    self._fetch_all_from_finnhub_endpoint,
                    self.finnhub_client.filings,
                    symbol=self.ticker,
                    batch_size=30
                ),
                'insider_transactions': executor.submit(
                    self._fetch_all_from_finnhub_endpoint,
                    self.finnhub_client.stock_insider_transactions,
                    symbol=self.ticker,
                    batch_size=30
                )
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
            f"sort=RELEVANCE&"
            f"time_from={date_utils.get_ISO_date_time(self.start_date)}&"
            f"limit=1000&"
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
    def _fetch_all_from_finnhub_endpoint(self, api_endpoint: Callable, batch_size: int = 7, **kwargs) -> List[Dict[str, Any]]:
        """
        Orchestrates multiple API calls for a given finnhub endpoint in batches. 
        Note: Finnhub has a current API limit of 25 calls/ second
        
        Args:
            api_endpoint (Callable): The Finnhub client method to call (e.g., self.finnhub_client.company_news).
            **kwargs: Keyword arguments to pass to the API endpoint method (e.g., symbol='AAPL').
        """
        all_data = []
        date_ranges = date_utils.get_dates_in_range(start_date=self.start_date, end_date=self.end_date, batch_size=batch_size)
        for from_date, to_date in date_ranges:
            try:
                batch_data = api_endpoint(_from=from_date, to=to_date, **kwargs)

                # For insider transactions endpoint, as it returns a dict -> Cannot extend!
                if isinstance(batch_data, dict) and 'data' in batch_data and isinstance(batch_data['data'], list):
                    all_data.extend(batch_data['data'])
                # default for most endpoints 
                elif isinstance(batch_data, list):
                    all_data.extend(batch_data)
            except Exception as e:
                print(f"Error fetching data for {api_endpoint.__name__} from {from_date} to {to_date}: {e}")
        return all_data
    
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
