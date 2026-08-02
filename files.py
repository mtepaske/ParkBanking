import pandas as pd
from account import Account
from transactions import Transaction


def cleanbanking(csv: pd.DataFrame) -> pd.DataFrame:
    csv.drop(labels=['Date', 'Account Number', 'Unnamed: 3', 'Merchant Name',
                     'Balance', 'Transaction Type', 'Category'],
             axis=1, inplace=True)
    csv.drop(csv[csv['Amount'] < 0].index, inplace=True, errors='ignore')
    return csv


def importPayments(csv: str) -> list[Transaction]:
    transactions = pd.read_csv(csv)
    cleanbanking(transactions)
    payments = []
    for transaction in transactions.index:
        date = transactions.loc[transaction]['Date']
        amount = transactions.loc[transaction]['Amount']
        details = transactions.loc[transaction]['Transaction Details']
        payments.append(Transaction(date, amount, details))
    return payments


def importAccounts(csv: str) -> list[Account]:
    accountscsv = pd.read_csv(csv, index_col='Site')
    accounts = []
    for site in accountscsv.index:
        name = accountscsv.loc[site]['Name']
        aliases = accountscsv.loc[site]['Aliases'].split(',')
        accounts.append(Account(site, name, aliases))
    return accounts


def importWordsToIgnore(csv: str) -> list[str]:
    wordsToIgnoreDF = pd.read_csv(csv)
    wordsToIgnore = []
    for word in wordsToIgnoreDF.index:
        wordsToIgnore.append(wordsToIgnoreDF.loc[word]['Words'])
    return wordsToIgnore


def exportAccounts(accounts: list[Account]):
    pass


def exportPayments(payments):
    pass


def exportWordsToIgnore(words: list[str]):
    df = pd.DataFrame({'Words': words})
    df.to_csv('WordsToIgnore.csv', index=False)
