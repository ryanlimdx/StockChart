from datetime import datetime, timedelta
from functools import singledispatch
from typing import Any, List

STANDARD_DATE_FORMAT = '%Y-%m-%d' # 'YYYY-MM-DD'
DISPLAY_DATE_FORMAT = '%b %d, %Y - %a' 
DISPLAY_TIME_FORMAT = '%H:%M'

ISO_DATETIME_FORMAT = '%Y%m%dT%H%M' # 'YYYYMMDDTHHMM'

#########################
# Datetime calculations #
#########################
def now() -> str:
    return datetime.now()

def backdate(past_days_ago: int) -> str:
    return datetime.now() - timedelta(days=past_days_ago)

def get_dates_in_range(start_date: datetime, end_date: datetime, batch_size: int = 7) -> List[tuple[str]]:
    """Generates a list of date strings between two dates."""
    ranges = []
    current_start = start_date
    
    while current_start <= end_date:
        current_end = min(current_start + timedelta(days=batch_size - 1), end_date)
        ranges.append((get_date(current_start), get_date(current_end)))
        
        current_start = current_end + timedelta(days=1)
        
    return ranges

#########################
# Date, time formatting #
#########################

@singledispatch
def get_date(date_input: Any = None) -> str:
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
    return date_obj.strftime(ISO_DATETIME_FORMAT)

####################
# Datetime display #
####################

def unix_to_display(unix_timestamp: int) -> tuple[str, str, str]:
    date_obj = datetime.fromtimestamp(unix_timestamp)

    std_date = date_obj.strftime(STANDARD_DATE_FORMAT)
    date = date_obj.strftime(DISPLAY_DATE_FORMAT)
    time = date_obj.strftime(DISPLAY_TIME_FORMAT)
    
    return std_date, date, time


# def str_todisplay(date_str: str)