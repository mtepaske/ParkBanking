from models.account import Account
from models.transactions import Transaction


def match_transactions(
    accounts: list[Account], transaction: Transaction, ignore: list[str]
) -> list[Account] | None:
    matcher = Matcher(accounts, ignore)
    possibilities = matcher.keyword_match(transaction)
    return possibilities


def process_payments(transactions: list[Transaction]) -> None:
    for transaction in transactions:
        if transaction.account is None:
            continue
        assert transaction.account.balance is not None
        transaction.account.balance.add_payment(transaction.amount)


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

    def keyword_match(self, transaction: Transaction) -> list[Account] | None:
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
        if len(possible) == 0:
            return None
        else:
            return possible

    def get_unknown_words(self) -> list[str]:
        return self.unknown
