import pandas as pd
from account import Account

def matchTransactions(transactions: pd.DataFrame, accounts: list[Account], wordsToIgnore: list[str]) -> Account|None:
    for transaction in transactions.index:
        description = transactions.loc[transaction]['Transaction Details'].split(' ')
        for word in description:
            if word in wordsToIgnore:
                print(f'{word} removed')
                description.remove(word)
        match = keywordMatch(description, accounts)
        if match == None:
            pass

def keywordMatch(description: list[str], accounts: list[Account], wordsToIgnore: list[str]) -> Account|None:
    wordsToAdd = []
    for word in description:
        print(f'WORD TO MATCH: {word}')
        for account in accounts:
#           print(f'ACCOUNT TO MATCH: {account}')
            aliases = account.getAlias()
            if word in aliases:
                return account
        user = input(f'Add {word} to Words To Ignore? (y/n)')
        if user == 'y':
            wordsToAdd.append(wordsToAdd)
    addToIgnore(wordsToAdd, wordsToIgnore)
    return None

def addToIgnore(words: list[str], wordsToIgnore: list[str]):
    return wordsToIgnore.extend(words)
