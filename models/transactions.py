from __future__ import annotations

from datetime import datetime as dt
from decimal import Decimal
from zoneinfo import ZoneInfo

from models.account import Account


def convert_date(date: str):  # Move to new service module to work with dates
    try:
        parsed_date = dt.strptime(date, "%d %b %y").astimezone(
            ZoneInfo("Australia/Melbourne")
        )
    except ValueError:
        parsed_date = dt.strptime(date, "%Y-%m-%d").astimezone(
            ZoneInfo("Australia/Melbourne")
        )
    return parsed_date.strftime("%Y-%m-%d")


class Transaction:
    """
    Represents a payment or charge

    Attributes:
        id: (int) The ID used for database queries. Gets assigned on first insertion to the database
        date: (str) The date of the transaction given in %Y-%m-%d or %d %b %y form
        amount: (Decimal) The monetary amount of the transaction
        account: (Account | None) The account the transaction is associated with. Defaults to None if no account associated
        original_details: (str) The details listed on the transaction
        details: (list[str]) A list containing the details for the transaction. Is cleaned during matching
        type: (str) A description of the type of transaction. Used for payment history and statement generating
    """

    account: None | Account

    def __init__(
        self,
        date: str,
        amount: Decimal,
        details: str,
        type_str: str = "",
        id: int | None = None,
    ) -> None:
        """
        Initialises the instance

        Args:
            date: The date of the transaction
            amount: The amount of the transaction
            details: The details of the transaction
            type: A description of the type of transaction. Defaults to None
            id: The ID used for database queries. Gets assigned on first insertion to database
        """

        self.id = id
        self.date = convert_date(date)
        self.amount = amount
        self.account = None
        self.original_details = details
        self.details = details.split(" ")
        self.type = type_str

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Transaction:
        """
        Constructs an instance from a row of a CSV file

        Args:
            row: The row of the CSV file

        Returns:
            The transaction instance containing the information
        """

        return cls(
            date=row["Date"],
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    @classmethod
    def from_matched_csv(
        cls, row: dict[str, str], accounts: list[Account]
    ) -> Transaction:
        """
        Constructs an instance from a row of a CSV file containing previously matched transactions

        Args:
            row: The row of the CSV file
            accounts: A list of accounts that the transaction may be matched too

        Returns:
            The transaction instance containing the information from the row
        """

        transaction = cls(
            row["Date"], Decimal(row["Amount"]), "previously matched"
        )  # Change dictionary to export original details

        # Matches the transaction to an account matching the site number
        for account in accounts:
            if account.site_number == row["Site"]:
                transaction.account = account
                break
        return transaction

    def to_dict(self) -> dict[str, str]:
        """
        Constructs a dictionary containing information required to reconstruct the transaction. Used for exporting to CSV

        Returns:
            A dictionary containing the transaction information
        """

        return {
            "Date": self.date,
            "Site": (
                str(self.account.site_number) if self.account is not None else "??"
            ),
            "Name": (self.account.name if self.account is not None else "Unmatched"),
            "Amount": str(self.amount),
            "Details": self.original_details,
        }

    def __str__(self) -> str:
        """
        A string representation of the account

        Returns:
            A string representation fo the account
        """

        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details} -> {self.account}"
