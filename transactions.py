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

    def __init__(self, date, amount: Decimal, details: str):
        """Initialises transaction

        Args:
            date: (str) The date of the payment
            amount: (int) The amount of the payment
            details: (str) the deatils for the payment
        """
        self.date = date
        self.amount = amount
        self.account = None
        self.details = details.split(" ")

    @classmethod
    def from_csv(cls, row):
        return cls(
            date=row["Date"],
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    def addAccount(self, account: Account):
        """Adds an account to the transaction

        Args:
            account: (Account) Account to add to the transaction
        """
        self.account = account

    def toDict(self) -> dict[str, str]:
        return {
            "Date": self.date,
            "Site": (self.account.site if self.account is not None else "??"),
            "Name": (self.account.name if self.account is not None else "Unmatched"),
            "Amount": str(self.amount),
        }

    def __str__(self):
        return f"Date: {self.date}, Amount: {self.amount}, Details: {self.details}"
