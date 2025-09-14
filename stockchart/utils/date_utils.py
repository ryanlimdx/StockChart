from datetime import datetime, timedelta
from functools import singledispatch
from typing import Any, List, Tuple

STANDARD_DATE_FORMAT = '%Y-%m-%d' # 'YYYY-MM-DD'
DISPLAY_DATE_FORMAT = '%b %d, %Y - %a' 
DISPLAY_TIME_FORMAT = '%H:%M'

ISO_DATETIME_FORMAT = '%Y%m%dT%H%M' # 'YYYYMMDDTHHMM'
ISO_DATETIME_WITH_SECONDS_FORMAT = '%Y%m%dT%H%M%S' # 'YYYYMMDDTHHMMSS'

# Datetime calculations

def now() -> str:
    """Return current datetime."""
    return datetime.now()

def backdate(past_days_ago: int) -> str:
    """Return a start datetime based on the period provided, counting back from current datetime."""
    return datetime.now() - timedelta(days=past_days_ago)

def get_dates_in_range(start_date: datetime, end_date: datetime, batch_size: int = 7) -> List[Tuple[str, str]]:
    """Generates a list of date ranges in reverse chronological order."""
    ranges = []
    current_end = end_date
    
    while current_end >= start_date:
        current_start = max(start_date, current_end - timedelta(days=batch_size - 1))
        ranges.append((get_date(current_start), get_date(current_end)))
        
        current_end = current_start - timedelta(days=1)
        
    return ranges

def is_exceed_duration(cache_date_time: str, comparable_date_time: str, duration_h: int) -> bool:
    """Check if the duration is exceed between 2 ISO Datetime strings."""
    difference = datetime.strptime(comparable_date_time, ISO_DATETIME_FORMAT) - datetime.strptime(cache_date_time, ISO_DATETIME_FORMAT)
    return difference > timedelta(hours=duration_h)

# Date, time formatting

@singledispatch
def get_date(date_input: Any = None) -> str:
    """Format the date input into a standard date string."""
    if date_input is None:
        return now().strftime(STANDARD_DATE_FORMAT)
    raise NotImplementedError(f"Cannot handle type {type(date_input)}")

@get_date.register(datetime)
def _(date_obj: datetime) -> str:
    return date_obj.strftime(STANDARD_DATE_FORMAT)

@get_date.register(str)
def _(date_str: str) -> str:
    try:
        date_obj = datetime.strptime(date_str, STANDARD_DATE_FORMAT)
    except ValueError:
        raise ValueError(f"Invalid date string format: {date_str}")
    return get_date(date_obj)

def get_ISO_date_time(date_obj: datetime) -> str:
    """Format the date input into an ISO date string."""
    return date_obj.strftime(ISO_DATETIME_FORMAT)

# Datetime display 

def unix_to_display(unix_timestamp: int) -> tuple[str, str, str]:
    """Converts a unix timestamp to a tuple of formatted date strings"""
    date_obj = datetime.fromtimestamp(unix_timestamp)

    std_date = date_obj.strftime(STANDARD_DATE_FORMAT)
    date = date_obj.strftime(DISPLAY_DATE_FORMAT)
    time = date_obj.strftime(DISPLAY_TIME_FORMAT)
    
    return std_date, date, time

def string_to_display(date_string: str) -> tuple[str, str, str]:
    """
    Converts a date string to a tuple of formatted date strings.
    """
    date_obj = None
    
    formats_to_try = [
        "%Y-%m-%d %H:%M:%S",
        STANDARD_DATE_FORMAT,
        ISO_DATETIME_FORMAT,
        ISO_DATETIME_WITH_SECONDS_FORMAT 
    ]
    
    for fmt in formats_to_try:
        try:
            date_obj = datetime.strptime(date_string, fmt)
            break
        except ValueError:
            continue
    
    if date_obj is None:
        raise ValueError("Unsupported date format.")
    
    std_date = date_obj.strftime(STANDARD_DATE_FORMAT)
    date = date_obj.strftime(DISPLAY_DATE_FORMAT)
    time = date_obj.strftime(DISPLAY_TIME_FORMAT)
    
    return std_date, date, time