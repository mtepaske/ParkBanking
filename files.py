import pandas as pd
from account import Account
from transactions import Transaction


def cleanbanking(csv: pd.DataFrame) -> pd.DataFrame:
    """Cleans a transaction data and removed irrelavent data

    Args:
        csv: (pd.DataFrame) A pandas data frame imported form a csv

    Returns:
        csv: (pd.DataFrame) A pandas data frame after cleaning
    """
    csv.drop(labels=['Date', 'Account Number', 'Unnamed: 3', 'Merchant Name',
                     'Balance', 'Transaction Type', 'Category'],
             axis=1, inplace=True)
    csv.drop(csv[csv['Amount'] < 0].index, inplace=True, errors='ignore')
    return csv


def importPayments(csv: str) -> list[Transaction]:
    """Import payment data from a CSV file

    Args:
        csv: (str) Name of the CSV file to import

    Returns:
        (list[Transaction]) A list of payments
    """
    transactions = pd.read_csv(csv)
    cleanbanking(transactions)
    payments = []
    for transaction in transactions.index:
        date = transactions.loc[transaction]['Processed On']
        amount = transactions.loc[transaction]['Amount']
        details = transactions.loc[transaction]['Transaction Details']
        payments.append(Transaction(date, amount, details))
    return payments


def importAccounts(csv: str) -> list[Account]:
    """Import account information from a CSV file

    Args:
        csv: (str) Name of the CSV file to import

    Returns:
        (list[Account]) A list of accounts
    """
    accountscsv = pd.read_csv(csv, index_col='Site')
    accounts = []
    for site in accountscsv.index:
        name = accountscsv.loc[site]['Name']
        aliases = accountscsv.loc[site]['Aliases'].split(',')
        accounts.append(Account(site, name, aliases))
    return accounts


def importWordsToIgnore(csv: str) -> list[str]:
    """Import words to ignore while matching from a CSV file

    Args:
        csv: (str) Name of the CSV file to import

    Returns:
        (list[str]) A list of words to ignore
    """
    wordsToIgnoreDF = pd.read_csv(csv)
    wordsToIgnore = []
    for word in wordsToIgnoreDF.index:
        wordsToIgnore.append(wordsToIgnoreDF.loc[word]['Words'])
    return wordsToIgnore


def exportAccounts(accounts: list[Account]):
    """Export a list of accounts to a CSV file

    Args:
        accounts: (list[Account]) A list of accounts
    """
    rows = [
        a.toDict()
        for a in accounts
    ]
    df = pd.DataFrame(rows)
    df.to_csv('Accounts.csv', index=False)


def exportPayments(payments: list[Transaction], filename: str):
    """Export a list of transactions with matched accounts to a CSV file

    Args:
        payments: (list[Transaction]) A list of transactions with matched accounts
        filename: (str) The name of the file on export
    """
    rows = [
        t.toDict()
        for t in payments
        if t.getAccount() is not None
    ]
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)


def exportWordsToIgnore(words: list[str]):
    """Export a list of words to ignore while matching to a CSV file

    Args:
        words: (list[str]) A list of words to ignore while matching
    """
    df = pd.DataFrame({'Words': words})
    df.to_csv('WordsToIgnore.csv', index=False)
