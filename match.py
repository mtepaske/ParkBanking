from account import Account
from transactions import Transaction


class Matcher:

    def __init__(self, accounts: list[Account], ignore: list[str]):
        self.accounts = accounts
        self.ignore = ignore
        self.unkown = []

    def cleanDesc(self, description: list[str]) -> list[str]:
        for word in description:
            if word in self.ignore:
                description.remove(word)
        return description

    def keywordMatch(self, transaction: Transaction):
        possible = []
        details = self.cleanDesc(transaction.details)
        for word in details:
            for account in self.accounts:
                if word in account.aliases:
                    possible.append(account)
                else:
                    self.unkown.append(word)
        return possible

    def match(self, transaction: Transaction, possibilities:
              list[Account | None]):
        if possibilities[0] is None:
            print('No Possible Matches Found')
        elif len(possibilities) == 1:
            transaction.addAccount(possibilities[0])
        else:
            pass
#           Insert user choice here
