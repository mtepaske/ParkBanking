from __future__ import annotations

from decimal import Decimal

from account import Account


class Transaction:
    """Stores and manipulates transaction data

    Attributes:
        date: (str) Date of patyment
        amount: (int) Amount of payment
        account:
            (None) If there is no account matched for transaction yet
            (Account) The account that is matched to the payment
        details: (list[str]) The details of the payment
    """

    def __init__(self, date, amount: Decimal, details: str) -> None:
        """Initialises transaction

        Args:
            date: (str) The date of the payment
            amount: (int) The amount of the payment
            details: (str) the deatils for the payment

        Returns:
            None
        """
        self.date = date
        self.amount = amount
        self.account = None
        self.details = details.split(" ")

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Transaction:
        """Converts from a csv row to a instance of the Transaction class

        Args:
            row: (dict[str, str]) A row of a csv file to convert

        Returns:
            None
        """
        return cls(
            date=row["Date"],
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    def add_account(self, account: Account) -> None:
        """Adds an account to the transaction

        Args:
            account: (Account) Account to add to the transaction

        Returns:
            None
        """
        self.account = account

    def to_dict(self) -> dict[str, str]:
        """Converts this instance of the Transaction class into a dictionary for exporting

        Returns:
            (dict[str, str]) A dictionary representing the Transaction class
        """
        return {
            "Date": self.date,
            "Site": (self.account.site if self.account is not None else "??"),
            "Name": (self.account.name if self.account is not None else "Unmatched"),
            "Amount": str(self.amount),
        }

    def __str__(self):
        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details}"
