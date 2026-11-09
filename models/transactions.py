from __future__ import annotations

from decimal import Decimal

from models.account import Account
from services.date import convert_to_iso


def match_transaction_on_account_id(
    transaction: Transaction, accounts: list[Account]
) -> None:

    for account in accounts:
        if transaction.account_id == account.account_id:
            transaction.account = account
            return


class Transaction:
    """
    Represents a payment or charge

    Attributes:
        date: (str) The date of the transaction given in %Y-%m-%d or %d %b %y form
        amount: (Decimal) The monetary amount of the transaction
        account: (Account | None) The account the transaction is associated with. Defaults to None if no account associated
        original_details: (str) The details listed on the transaction
        details: (list[str]) A list containing the details for the transaction. Is cleaned during matching
        type: (str) A description of the type of transaction. Used for payment history and statement generating
        account_id: (int) The Account ID of the account that this transaction is matched too. Used for database queries. Gets assigned on accounts first insertion
        transaction_id: (int) The ID used for database queries. Gets assigned on first insertion to the database
    """

    account: None | Account

    def __init__(
        self,
        date: str,
        amount: Decimal,
        details: str = "",
        type_str: str = "",
        account: Account | None = None,
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
            account_id: The Account ID of the account that this transaction is matched too. Used for database queries. Gets assigned on accounts first insertion
            transaction_id: The ID used for database queries. Gets assigned on first insertion to the database
        """

        self.date = convert_to_iso(date)
        self.amount = amount
        self.account = account
        self.details = details
        self.type = type_str
        self.account_id = account_id
        self.transaction_id = transaction_id

        if self.account is not None:
            self.account_id = self.account.account_id

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

        # Construct the class
        transaction = cls(
            date=date,
            amount=Decimal(amount),
            details=details,
            account_id=account_id,
            transaction_id=transaction_id,
        )

        for account in accounts:

            # Attempts to match off account_id if one exists
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

    @classmethod
    def from_history_csv(cls, row: dict[str, str], account: Account) -> Transaction:
        """
        Constructs an instance from a row of a CSV file containing a history of charges and payments

        Args:
            row: The row of the CSV file
            account: The account that the history is for

        Returns:
            The transaction instance containing the information
        """
        date = row["Date"]
        description = row["Description"]
        debit = row["Debit"]
        credit = row["Credit"]

        # Construct the class
        transaction = Transaction(
            date=date,
            amount=Decimal(credit) if credit != "" else Decimal(0 - Decimal(debit)),
            type_str=description,
        )

        # Sets the matched account and account_id
        transaction.account = account
        transaction.account_id = account.account_id

        return transaction

    def add_account(self, account: Account) -> None:
        """
        Add an account to this transaction

        Args:
            account: The account to add
        """

        self.account = account
        self.account_id = account.account_id

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
            "Details": self.details,
            "Account ID": (
                str(self.account.account_id) if self.account is not None else "??"
            ),
            "Transaction ID": (
                str(self.transaction_id) if self.transaction_id is not None else "None"
            ),
        }

    def __str__(self) -> str:
        """
        A string representation of the transaction

        Returns:
            A string representation fo the transaction
        """

        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details} -> {self.account}"
