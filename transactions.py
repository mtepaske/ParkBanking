from account import Account


class Transaction:

    def __init__(self, date, amount: int, details: str):
        self.date = date
        self.amount = amount
        self.account = None
        self.details = details.split(' ')

    def addAccount(self, account: Account):
        self.account = account
#       print(f'{account} Added to transaction')

    def getAccount(self):
        return self.account

    def toDict(self) -> None | dict:
        if self.account is None:
            return None
        return {
            'Date': self.date,
            'Site': self.account.getSite(),
            'Name': self.account.getName(),
            'Amount': self.amount
        }
