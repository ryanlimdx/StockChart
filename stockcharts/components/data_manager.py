import pandas as pd
from enum import Enum, IntEnum
from typing import Dict, Any, List, Generator
from stockcharts.api.data_fetcher import DataFetcher
from stockcharts.utils import date_utils

class DataManager:
    """Handles fetching and processing of all financial data."""
    def __init__(self, ticker: str = "NVDA"):
        self.ticker = ticker
        self.data_fetcher = DataFetcher(ticker=ticker)

    def load_price_data(self) -> pd.DataFrame:
        """Fetches raw price data in parallel."""
        price_future = self.data_fetcher.fetch_price_async()
        price = price_future.result()
        return price
    
    def load_event_data(self) -> List[Dict[str, Any]]:
        raw_events = self._fetch_event_data()
        processed_events = self._process_events(events=raw_events)
        return processed_events
    
    def _process_events(self, events: Dict[str, Any]) -> List[Dict[str, Any]]:
        preprocessed_event_gen = self._preprocess_events(events=events)
        # TODO: Process events here
        return list(preprocessed_event_gen)

    def _preprocess_events(self, events: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Performs data transformation, preprocessing one by one, to conform to a standard format.
        Returns an event.
        """

        # https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo
        macro_news_data = events.get('macro_news', {}).get('feed', [])
        for m in macro_news_data:
            score = EventType.MACRO_NEWS.base_score
            ticker_sentiment_list = m.get('ticker_sentiment', [])

            ticker_sentiments = {s['ticker']: s for s in ticker_sentiment_list}
            sentiment = ticker_sentiments.get(self.ticker, {})
            relevance = float(sentiment.get('relevance_score', 0))
            score *= (1 + relevance)

            std_date, date, time = date_utils.string_to_display(m['time_published'])
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'type': EventType.MACRO_NEWS.name, 
                'title': m['title'],
                'content': m['summary'],
                'source': f"🔗 {m['source']}",
                'url': m['url'],
                'importance_rank': score
            }

        # https://finnhub.io/docs/api/company-news
        company_news_data = events.get('company_news', [])
        for n in company_news_data:
            std_date, date, time = date_utils.unix_to_display(n['datetime'])
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'type': EventType.COMPANY_NEWS.name, 
                'title': n['headline'],
                'content': n['summary'],
                'source': f"🔗 {n['source']}",
                'url': n['url'],
                'importance_rank': EventType.COMPANY_NEWS.base_score
            }
        
        # https://finnhub.io/docs/api/filings
        sec_filings_data = events.get('filings', [])
        for f in sec_filings_data:
            std_date, date, time = date_utils.string_to_display(f['filedDate'])
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'type': EventType.SEC_FILING.name, 
                'title': f"Form {f['form']}",
                'content': f"{self.ticker} SEC Filing",
                'source': "🔗 SEC",
                'url': f['reportUrl'],
                'importance_rank': EventType.SEC_FILING.base_score
            }

        # https://finnhub.io/docs/api/insider-transactions
        insider_transactions_data = events.get('insider_transactions', [])
        for i in insider_transactions_data:
            std_date, date, time = date_utils.string_to_display(i['transactionDate'])
            action = "increases" if i['change'] > 0 else "decreases"
            title_string=f"{i['name']} {action} shares in {self.ticker}"
            content_string=f"Transaction code: {i['transactionCode']}\nTransaction price: {i['transactionPrice']}\nCurrent stake: {i['share']} shares"
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'type': EventType.INSIDER_TRANSACTION.name, 
                'title': f"{title_string}",
                'content': f"{content_string}",
                'source': "🔗 List of Transaction codes (Section 8)",
                'url': "https://www.sec.gov/about/forms/form4data.pdf",
                'importance_rank': EventType.INSIDER_TRANSACTION.base_score
            }

    def _fetch_event_data(self) -> Dict[str, Any]:
        """Fetches raw event data in parallel."""
        event_futures = self.data_fetcher.fetch_events_async()
        events = {}
        for key, future in event_futures.items():
            events[key] = future.result()
        return events

    def day_events(self, events: List[Dict[str, Any]], date: str = None) -> Dict[str, Any]:
        """Returns only the current date's events."""
        selected_date = date_utils.get_date(date)
        all_day_events = [e for e in events if e['std_date'] == selected_date]
        return self._filter_events(all_day_events)
    
    def _filter_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Filters the event list."""
        if len(events) > 20:
            sorted_events = sorted(events, key=lambda x: int(x.get('importance_rank', 0)), reverse=True)
            events = sorted_events[:20]
        return events

class EventType(Enum):
    """
    Defines the types of events with associated string and base scores.
    """
    def __new__(cls, name: str, base_score: float):
        obj = object.__new__(cls)
        obj._value_ = name
        obj._event_name = name
        obj.base_score = base_score
        return obj

    @property
    def name(self):
        return self._event_name

    MACRO_NEWS = "Macro News", 0.4
    COMPANY_NEWS = "News", 0.6
    INSIDER_TRANSACTION = "Insider Transaction", 1.0
    SEC_FILING = "SEC Filing", 0.8

if __name__ == '__main__':
    DataManager(ticker="NVDA")