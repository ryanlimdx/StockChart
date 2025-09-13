import pandas as pd
from enum import Enum, IntEnum
from typing import Dict, Any, List, Generator
from stockcharts.api.data_fetcher import DataFetcher
from stockcharts.utils import date_utils
from itertools import groupby
import os
import json

class DataManager:
    """Handles fetching and processing of all financial data."""
    def __init__(self, ticker: str = "NVDA"):
        self.ticker = ticker
        self.data_fetcher = DataFetcher(ticker=ticker)
        self._cache_dir = "cache"
        os.makedirs(self._cache_dir, exist_ok=True)

    def load_price_data(self) -> pd.DataFrame:
        """Fetches raw price data in parallel."""
        price_future = self.data_fetcher.fetch_price_async()
        price = price_future.result()
        return price
    
    def load_event_data(self) -> List[Dict[str, Any]]:
        """Fetches raw event data and processes them."""
        cache_path = os.path.join(self._cache_dir, f"{self.ticker}_events.json")

        # Check if a valid, non-stale cache entry exists
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                try:
                    cached_data = json.load(f)
                    # Check if the cache is older than the specified duration
                    if not date_utils.is_exceed_duration(
                        cache_date_time=cached_data.get('timestamp'),
                        comparable_date_time=date_utils.get_ISO_date_time(date_obj=date_utils.now()),
                        duration_h=6
                        ):
                        return cached_data.get('data')
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                    print(f"Error reading cache file for {self.ticker}, or it's in an old format: {e}. Fetching new data.")
        print("No cached data")
        raw_events = self._fetch_event_data()
        processed_events = list(self._process_events(events=raw_events))

        data_to_save = {
            'data': processed_events,
            'timestamp': date_utils.get_ISO_date_time(date_obj=date_utils.now())
        }
        with open(cache_path, 'w') as f:
            json.dump(data_to_save, f)
        return processed_events

    def _process_events(self, events: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Performs data transformation, preprocessing one by one, to conform to a standard format:
        {
            'std_date': the standard date format,
            'date': the display date format,
            'time': the display time format, if available,
            'type': the event type,
            'title': the title of the content,
            'content': the (short) summary of the content,
            'source': the source,
            'url': the link to the event/ article,
            'importance_rank': score (for ranking)
        }
        Yields a single event.
        """
        yield from self._process_macro_news(events.get('macro_news', {}).get('feed', []))
        yield from self._process_company_news(events.get('company_news', []))
        yield from self._process_sec_filings(events.get('filings', []))
        yield from self._process_insider_transactions(events.get('insider_transactions', []))

    def _process_macro_news(self, news_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Yields an event that conforms to the standard format."""
        yield from self._preprocess_macro_news(news_data=news_data)

    def _process_company_news(self, news_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Yields an event that conforms to the standard format."""
        yield from self._preprocess_company_news(news_data=news_data)

    def _process_sec_filings(self, filings_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Yields an event that conforms to the standard format."""
        yield from self._preprocess_sec_filings(filings_data=filings_data)

    def _process_insider_transactions(self, transactions_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """
        Processes and aggregates insider transactions, yielding a single aggregated event (for each day).
        Yields an event that conforms to the standard format.
        """
        transactions = list(self._preprocess_insider_transactions(transactions_data=transactions_data))
        
        aggregated_events = []

        keyfunc = lambda e: (e['std_date'], e['name'])
        transactions.sort(key=keyfunc)

        # Aggregate transactions made by the same name (person) on the same day
        for (std_date, name), group in groupby(transactions, key=keyfunc):
            group_list = list(group)
            total_change = sum(item['change'] for item in group_list)

            if total_change == 0:
                continue

            total_value = sum(item['change'] * item['transactionPrice'] for item in group_list)
            avg_price = total_value / total_change
            
            first_event = group_list[0] # Used as template
            action = "net acquired" if total_change > 0 else "net disposed of"
            
            aggregated_event = {
                'std_date': std_date,
                'date': first_event['date'],
                'time': '', 
                'type': EventType.INSIDER_TRANSACTION.name,
                'title': f"{name} {action} {abs(total_change)} shares in {self.ticker}",
                'content': f"Summary of all transactions on this day.\nAverage price: ${avg_price:.2f}",
                'source': first_event['source'],
                'url': first_event['url'],
                'importance_rank': EventType.INSIDER_TRANSACTION.base_score
            }
            aggregated_events.append(aggregated_event)
        
        yield from aggregated_events

    def _preprocess_macro_news(self, news_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Preprocesses and yields macro news events."""
        for m in news_data:
            if not m.get('title') or not m.get('summary') or not m.get('time_published'):
                continue

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

    def _preprocess_company_news(self, news_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Preprocesses and yields company news events."""
        for n in news_data:
            if not n.get('headline') or not n.get('summary') or not n.get('datetime'):
                continue
            
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

    def _preprocess_sec_filings(self, filings_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Preprocesses and yields SEC filing events."""
        for f in filings_data:
            if not f.get('form') or not f.get('filedDate') or not f.get('reportUrl'):
                continue

            std_date, date, time = date_utils.string_to_display(f['filedDate'])
            yield {
                'std_date': std_date,
                'date': date,
                'time': '',
                'type': EventType.SEC_FILING.name, 
                'title': f"Form {f['form']}",
                'content': f"{self.ticker} SEC Filing",
                'source': "🔗 SEC",
                'url': f['reportUrl'],
                'importance_rank': EventType.SEC_FILING.base_score
            }

    def _preprocess_insider_transactions(self, transactions_data: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Preprocesses and yields insider transaction events."""
        for i in transactions_data:
            if not i.get('transactionDate') or not i.get('share') or not i.get('change') or not i.get('name') or not i.get('transactionPrice') or not i.get('transactionCode'):
                continue
            
            std_date, date, time = date_utils.string_to_display(i['transactionDate'])
            action = "increases" if i['change'] > 0 else "decreases"
            title_string=f"{i['name']} {action} shares in {self.ticker}"
            content_string=f"Transaction code: {i['transactionCode']}\nTransaction price: {i['transactionPrice']}\nCurrent stake: {i['share']} shares"
            yield {
                'std_date': std_date,
                'date': date,
                'time': time,
                'name': i.get('name'),
                'type': EventType.INSIDER_TRANSACTION.name, 
                'title': f"{title_string}",
                'content': f"{content_string}",
                'change': i.get('change'),
                'transactionPrice': i.get('transactionPrice'),
                'source': "🔗 List of Transaction Codes (Section 8)",
                'url': "https://www.sec.gov/about/forms/form4data.pdf",
                'importance_rank': EventType.INSIDER_TRANSACTION.base_score
            }

    def _fetch_event_data(self) -> Dict[str, Any]:
        """Fetches raw event data."""
        event_futures = self.data_fetcher.fetch_events_async()
        events = {}
        for key, future in event_futures.items():
            events[key] = future.result()
        return events

    def day_events(self, events: List[Dict[str, Any]], date: str = None) -> Dict[str, Any]:
        """Returns only the current date's events."""
        selected_date = date_utils.get_date(date)
        all_day_events = [e for e in events if e['std_date'] == selected_date]
        return self._top_events(all_day_events)
    
    def _top_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Filters the day's event list to the top 20."""
        if len(events) > 20:
            sorted_events = sorted(events, key=lambda x: int(x.get('importance_rank', 0)), reverse=True)
            events = sorted_events[:10]
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
    SEC_FILING = "SEC Filing", 1.0

if __name__ == '__main__':
    DataManager(ticker="NVDA")