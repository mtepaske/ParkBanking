from __future__ import annotations

from decimal import Decimal

from models.account import Account


class Transaction:
    def __init__(self, date, amount: Decimal, details: str) -> None:
        self.date = date
        self.amount = amount
        self.account = None
        self.details = details.split(" ")

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Transaction:
        return cls(
            date=row["Date"],
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    @classmethod
    def from_matched(cls, row: dict[str, str], accounts: list[Account]) -> Transaction:
        transaction = cls(row["Date"], Decimal(row["Amount"]), "previously matched")
        for account in accounts:
            if account.site == row["Site"]:
                transaction.add_account(account)
                break
        return transaction

    def add_account(self, account: Account) -> None:
        self.account = account

    def to_dict(self) -> dict[str, str]:
        return {
            "Date": self.date,
            "Site": (str(self.account.site) if self.account is not None else "??"),
            "Name": (self.account.name if self.account is not None else "Unmatched"),
            "Amount": str(self.amount),
        }

    def __str__(self):
        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details} -> {self.account}"
