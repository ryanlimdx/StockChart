from datetime import datetime, timedelta

def format_date(date_obj: datetime) -> str:
    """Formats a datetime object to a 'YYYY-MM-DD' string."""
    return date_obj.strftime('%Y-%m-%d')

def now() -> str:
    return format_date(datetime.now())

def backdate(past_days_ago: int) -> str:
    past_date = datetime.now() - timedelta(days=past_days_ago)
    return format_date(past_date)
