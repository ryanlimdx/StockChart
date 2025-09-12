from datetime import datetime, timedelta

def get_date(date_obj: datetime) -> str:
    """Formats a datetime object to a 'YYYY-MM-DD' string."""
    return date_obj.strftime('%Y-%m-%d')

def get_date_time(date_obj: datetime) -> str:
    """Formats a datetime object to 'YYYYMMDDTHHMM' string."""
    return date_obj.strftime('%Y%m%dT%H%M')

def now() -> str:
    return datetime.now()

def backdate(past_days_ago: int) -> str:
    return datetime.now() - timedelta(days=past_days_ago)

def unix_to_display(unix_timestamp: int) -> tuple[str, str, str]:
    date_obj = datetime.fromtimestamp(unix_timestamp)

    std_date = date_obj.strftime('%Y-%m-%d')
    date = date_obj.strftime("%d %m %Y, %a")
    time = date_obj.strftime("%H:%M")
    
    return std_date, date, time
