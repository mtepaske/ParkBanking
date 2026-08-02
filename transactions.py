from account import Account


class Transaction:

    def __init__(self, date, amount: int, details: str):
        self.date = date
        self.amount = amount
        self.account = None
        self.details = details.split(' ')

    def addAccount(self, account: Account):
        self.account = account

    def getAccount(self):
        return self.account
