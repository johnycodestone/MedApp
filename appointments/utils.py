from datetime import datetime
from django.utils import timezone


def parse_datetime(datetime_str):
    """
    Convert string to datetime object.
    Supports ISO 8601 and common formats.
    Returns None if parsing fails.
    """
    if not datetime_str:
        return None

    try:
        # First try ISO 8601
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        pass

    # Try common fallback formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    return None


def format_datetime_for_display(dt):
    """
    Format a datetime for user-friendly display in templates.
    Example: 'Sunday, Nov 23 at 06:30 PM'
    """
    if not dt:
        return "—"
    local_dt = timezone.localtime(dt)
    return local_dt.strftime("%A, %b %d at %I:%M %p")


def is_future_datetime(dt):
    """
    Check if a datetime is in the future relative to now.
    """
    if not dt:
        return False
    return dt > timezone.now()
