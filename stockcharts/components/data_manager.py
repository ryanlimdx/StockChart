import pandas as pd
from typing import Dict, Any, Generator
from stockcharts.api.data_fetcher import DataFetcher
from stockcharts.utils import date_utils

class DataManager:
    """Handles fetching and processing of all financial data."""
    def __init__(self, ticker: str = "NVDA"):
        self.ticker = ticker
        self.data_fetcher = DataFetcher(ticker=ticker)

    def fetch_raw_data(self) -> tuple[pd.DataFrame,  Dict[str, Any]]:
        """Fetches raw data in parallel."""
        futures = self.data_fetcher.fetch_data_async()

        price = None
        events = {}

        for key, future in futures.items():
            if key == 'price':
                price = future.result()
                continue
            events[key] = future.result()
        return price, events

    def process_events(self, events: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """Performs data transformation one by one, to conform to a standard format."""
        company_news_data = events.get('company_news', [])
        for n in company_news_data:
            std_date, date, time = date_utils.unix_to_display(n['datetime'])
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'type': 'News', 
                'content': n['headline'],
                'importance_rank': '1'
            }

    def day_events(self, events: Dict[str, Any], date: str = None) -> Dict[str, Any]:
        """Returns only the current date's events."""
        selected_date = date_utils.get_date(date)
        all_day_events = [e for e in events if e['std_date'] == selected_date]
        return self.filter_events(all_day_events)
    
    def filter_events(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """Filters the event list."""
        if len(events) > 5:
            sorted_events = sorted(events, key=lambda x: int(x.get('importance_rank', 0)), reverse=True)
            events = sorted_events[:5]
        return events


if __name__ == '__main__':
    DataManager(ticker="NVDA")