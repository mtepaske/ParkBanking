import csv
from decimal import Decimal

import transactions
from account import Account
from transactions import Transaction


def importPayments(filepath: str):
    transactions = []
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if Decimal(row["Amount"]) < 0:
                continue
            transactions.append(Transaction.from_csv(row))
    return transactions


def importAccounts(filepath: str) -> list[Account]:
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [Account.from_csv(row) for row in reader]


def importWordsToIgnore(filepath: str) -> list[str]:
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [row["Words"] for row in reader]


def exportAccounts(accounts: list[Account]):
    fieldnames = ["Name", "Site", "Aliases"]
    with open("Accounts.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            writer.writerow(account.toDict())


def exportPayments(payments: list[Transaction], filename: str):
    fieldnames = ["Date", "Site", "Name", "Amount"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in payments:
            writer.writerow(transaction.toDict())


def exportWordsToIgnore(words: list[str]):
    with open("WordsToIgnore.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])
        for word in words:
            writer.writerow([word])


if __name__ == "__main__":

    transactions = importPayments("Transactions.csv")
    for transaction in transactions:
        print(transaction)
