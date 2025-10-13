from datetime import datetime

def parse_datetime(datetime_str):
    """Convert string to datetime object."""
    try:
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        return None
