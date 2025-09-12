from datetime import datetime, timedelta

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

#########################
# Datetime formatting   #
#########################

def get_date(date_obj: datetime = now()) -> str:
    return date_obj.strftime(STANDARD_DATE_FORMAT)

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
