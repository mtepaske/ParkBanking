import pandas as pd
from account import Account

class Transaction:

    def __init__(self, date, amount: int, details: str):
        self.date = date
        self.amount = amount
        self.account = None

    def addAccount(self, account: Account):
        self.account = Account

    def cleanDetails(self, details: str):
        detailsList = details.split(' ')
        
        

