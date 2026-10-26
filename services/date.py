from datetime import date
from datetime import datetime as dt
from zoneinfo import ZoneInfo


def get_today() -> date:
    """
    Gets todays date

    Returns:
        Todays date
    """
    return dt.now(ZoneInfo("Australia/Melbourne")).date()


def start_of_fy(day: date | None = None) -> date:
    """
    Finds the start of the fincial year

    Args:
        day: The date

    Returns:
        The start of the FY
    """
    if day is None:
        day = get_today()

    if day.month >= 7:
        return date(day.year, 7, 1)
    else:
        return date(day.year - 1, 7, 1)


def end_of_fy(day: date | None = None) -> date:
    """
    Finds the end of the fincial year

    Args:
        day: The date

    Returns:
        The end of the FY
    """

    if day is None:
        day = get_today()

    if day.month >= 7:
        return date(day.year + 1, 6, 30)
    else:
        return date(day.year, 6, 30)


def convert_to_iso(date: str):
    """
    Converts a date string into a ISO format

    Args:
        date: The date string

    Returns:
        The date in ISO format
    """
    try:
        parsed_date = dt.strptime(date, "%d %b %y").astimezone(
            ZoneInfo("Australia/Melbourne")
        )
    except ValueError:
        parsed_date = dt.strptime(date, "%Y-%m-%d").astimezone(
            ZoneInfo("Australia/Melbourne")
        )
    return parsed_date.strftime("%Y-%m-%d")
