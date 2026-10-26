from datetime import date
from datetime import datetime as dt
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta


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


def convert_to_iso(date: str) -> str:
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


def get_last_month(day: date | None = None) -> str:
    """
    Gets the month before a given date

    Args:
        day: The date to get the month before

    Returns:
        The number representation of the previous month
    """

    if day is None:
        day = get_today()

    last_month_date = day - relativedelta(months=1)
    return last_month_date.strftime("%B")


def get_last_month_year(day: date | None = None) -> str:
    """
    Gets the year of the month before a given date

    Args:
        day: The date to get the month before

    Returns:
        The number representation of year of the previous month
    """

    if day is None:
        day = get_today()

    last_month_date = day - relativedelta(months=1)
    return last_month_date.strftime("%Y")


def get_date_from_str(date: str) -> date:
    """
    Converts from a string to a date

    Args:
        date: The date to convert

    Returns:
        The date as a date object
    """

    try:
        parsed_date = dt.strptime(date, "%d %b %y").astimezone(
            ZoneInfo("Australia/Melbourne")
        )
    except ValueError:
        parsed_date = dt.strptime(date, "%Y-%m-%d").astimezone(
            ZoneInfo("Australia/Melbourne")
        )

    return parsed_date


def get_str_from_date(date: date) -> str:
    """
    Converts a date to a string in ISO format

    Args:
        date: The date to convert

    Returns:
        The date in ISO format
    """

    return date.strftime("%Y=%m-%d")


def get_date_from_str_iso(date: str) -> date:
    """
    Converts from a string in ISO format to a date

    Args:
        date: The date to convert

    Returns:
        The date as a date object
    """

    parsed_date = dt.strptime(date, "%Y-%m-%d").astimezone(
        ZoneInfo("Australia/Melbourne")
    )

    return parsed_date
