from typing import Dict, Any, Generator
from stockcharts.api.data_fetcher import DataFetcher
from stockcharts.utils import date_utils

class DataManager:
    """Handles fetching and processing of all financial data."""
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.data_fetcher = DataFetcher(ticker=ticker)
        self.price_data = None
        self.events_data = []

    def load_and_process_data(self):
        """Fetches raw data and processes it."""
        futures = self.data_fetcher.fetch_data_async()

        raw_data = {}
        for key, future in futures.items():
            raw_data[key] = future.result()

        self.price_data = raw_data.get('prices')
        
        event_gen = self._process_events(raw_data)
        self.events = [e for e in event_gen]

    def _process_events(self, raw_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        company_news_data = raw_data.get('company_news', [])
        
        for n in company_news_data:
            std_date, date, time = date_utils.unix_to_display(n['datetime'])
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'type': 'News', 
                'content': n['headline']
            }
            print(f"  - Processed news item: '{n['headline']}'")

if __name__ == '__main__':
    DataManager(ticker="NVDA").load_and_process_data()