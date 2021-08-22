from datetime import datetime, timezone


def get_iso_date_from_ms_timestamp(timestamp: int) -> str:
    """
    Transforms an ms-accuracy timestamp to a s-accurate ISO datetime string
    """
    date_time = datetime.utcfromtimestamp(timestamp / 1000).replace(tzinfo=timezone.utc)
    return date_time.isoformat(timespec="seconds")
