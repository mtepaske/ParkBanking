from __future__ import annotations

from datetime import datetime as dt
from decimal import Decimal
from zoneinfo import ZoneInfo

from models.account import Account


def convert_date(date: str):
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
    def __init__(
        self,
        date: str,
        amount: Decimal,
        details: str,
        particulars: str = "",
        proccessed: bool = False,
        id: int | None = None,
    ) -> None:
        self.id = id
        self.date = convert_date(date)
        self.amount = amount
        self.account = None
        self.original_details = details
        self.particulars = particulars
        self.details = details.split(" ")
        self.proccessed = proccessed

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Transaction:
        return cls(
            date=row["Date"],
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    @classmethod
    def from_matched_csv(
        cls, row: dict[str, str], accounts: list[Account]
    ) -> Transaction:
        transaction = cls(row["Date"], Decimal(row["Amount"]), "previously matched")
        for account in accounts:
            if account.site_number == row["Site"]:
                transaction.add_account(account)
                break
        return transaction

    def add_account(self, account: Account) -> None:
        self.account = account

    def to_dict(self) -> dict[str, str]:
        return {
            "Date": self.date,
            "Site": (
                str(self.account.site_number) if self.account is not None else "??"
            ),
            "Name": (self.account.name if self.account is not None else "Unmatched"),
            "Amount": str(self.amount),
            "Details": self.original_details,
        }

    def __str__(self):
        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details} -> {self.account}"
