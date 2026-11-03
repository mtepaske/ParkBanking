from __future__ import annotations

from decimal import Decimal

from models.account import Account
from services.date import convert_to_iso


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
        account_id: int | None = None,
        transaction_id: int | None = None,
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

        self.date = convert_to_iso(date)
        self.amount = amount
        self.account = None
        self.original_details = details
        self.details = details.split(" ")
        self.type = type_str
        self.account_id = account_id
        self.transaction_id = transaction_id

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

        date = row["Date"]
        site_number = row["Site Number"]
        name = row["Name"]
        amount = row["Amount"]
        details = row["Details"]
        account_id = row["Account ID"]
        transaction_id = row["Transaction ID"]

        # Checks for and normalises the account ID. If none is found it assigns None
        if account_id == "None" or account_id == "":
            account_id = None
        else:
            account_id = int(account_id)

        # Checks for and normalises the transaction ID. If none is found it assigns None
        if transaction_id == "None" or transaction_id == "":
            transaction_id = None
        else:
            transaction_id = int(transaction_id)

        transaction = cls(
            date=date,
            amount=Decimal(amount),
            details=details,
            account_id=account_id,
            transaction_id=transaction_id,
        )

        for account in accounts:

            # Attempts to match of account_id if one exists
            if transaction.account_id is not None:
                if account.account_id == transaction.account_id:
                    transaction.account = account
                    break

            # Falls back on site_number and name
            elif account.site_number == site_number and account.name == name:
                transaction.account = account
                transaction.account_id = account.account_id
                break

        return transaction

    def to_dict(self) -> dict[str, str]:
        """
        Constructs a dictionary containing information required to reconstruct the transaction. Used for exporting to CSV

        Returns:
            A dictionary containing the transaction information
        """

        # Construct the Dictionary
        return {
            "Date": self.date,
            "Site Number": (
                str(self.account.site_number) if self.account is not None else "??"
            ),
            "Name": (self.account.name if self.account is not None else "Unmatched"),
            "Amount": str(self.amount),
            "Details": self.original_details,
            "Account ID": (
                str(self.account.account_id) if self.account is not None else "??"
            ),
            "Transaction ID": (
                str(self.transaction_id) if self.transaction_id is not None else "None"
            ),
        }

    def __str__(self) -> str:
        """
        A string representation of the account

        Returns:
            A string representation fo the account
        """

        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details} -> {self.account}"
