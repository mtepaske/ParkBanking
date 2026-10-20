from decimal import Decimal

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction


class Matcher:

    def __init__(self, accounts: list[Account], ignore: list[str]) -> None:
        self.accounts = accounts
        self.ignore = ignore
        self.unknown = []

    def clean_desc(self, description: list[str]) -> list[str]:
        filtered = []
        for word in description:
            if word not in self.ignore:
                filtered.append(word)
        return filtered

    def keyword_match(self, transaction: Transaction) -> list[Account]:
        possible = []
        details = self.clean_desc(transaction.details)
        for word in details:
            found = False
            for account in self.accounts:
                if word in account.aliases:
                    found = True
                    if account not in possible:
                        possible.append(account)
            if found is False and self.unknown is not None:
                for unknown in self.unknown:
                    if word == unknown:
                        break
                self.unknown.append(word)
        return possible

    def get_unknown_words(self) -> list[str]:
        return self.unknown


def match_transactions(matcher: Matcher, transaction: Transaction) -> list[Account]:
    possibilities = matcher.keyword_match(transaction)
    return possibilities


def review_payment(
    balance: Balance, amount: Decimal
) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    new_remaining = balance.remaining
    new_outstanding = balance.outstanding
    new_credit = balance.credit
    amount = balance.money(amount)
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")
    if amount < new_outstanding:
        new_outstanding -= amount
    elif amount < balance.balance:
        amount -= new_outstanding
        new_outstanding = Decimal("0.00")
        new_remaining -= amount
    else:
        amount -= new_outstanding
        new_outstanding = Decimal("0.00")
        amount -= new_remaining
        new_remaining = Decimal("0.00")
        new_credit = amount
    old_v_new = (
        {
            "Remaining": balance.remaining,
            "Outstanding": balance.outstanding,
            "Credit": balance.credit,
        },
        {
            "Remaining": new_remaining,
            "Outstanding": new_outstanding,
            "Credit": new_credit,
        },
    )
    return old_v_new
