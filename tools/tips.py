import sys
import random
def exit():
    sys.exit()
    
from datetime import datetime, timedelta, timezone
def timestamp2timestr(timestamp: int):
    # timestamp = 1722701089000
    timestamp_seconds = timestamp / 1000
    utc_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    china_time = utc_time.astimezone(timezone(timedelta(hours=8)))
    formatted_time = china_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

def random_time(start=2,end=6):
    return random.randint(start,end)

if __name__ == "__main__":
    print(random_time())