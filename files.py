import csv
from decimal import Decimal

from account import Account
from balance import Balance
from transactions import Transaction


def importPayments(filepath: str) -> list[Transaction]:
    """Imports relavent transaction information from a csv as a Transaction class

    Args:
        filepath: (str) The name of the file to import

    Returns:
        (list[Transaction]) A list of imported transactions
    """
    transactions = []
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if Decimal(row["Amount"]) < 0:
                continue
            transactions.append(Transaction.from_csv(row))
    return transactions


def importAccounts(filepath: str) -> list[Account]:
    """Import a csv containing account information as Account classes

    Args:
        filepath: (str) The name of the file to import

    Returns:
        (list[Account]) A list of imported accounts
    """
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [Account.from_csv(row) for row in reader]


def importWordsToIgnore(filepath: str) -> list[str]:
    """Import a csv containing words to ignore

    Args:
        filepath: (str) The name of the file to import

    Returns:
        (list[str]) A list of words to ignore
    """
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [row["Words"] for row in reader]


def import_balances(filepath: str) -> list[Balance]:
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [Balance.from_csv(row) for row in reader]


def exportAccounts(accounts: list[Account]) -> None:
    """Export updated account information as a csv file

    Args:
        accounts: (list[Account]) A list of accounts to export

    Returns:
        None
    """
    fieldnames = ["Name", "Site", "Aliases"]
    with open("Accounts.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            writer.writerow(account.toDict())


def exportPayments(payments: list[Transaction], filename: str) -> None:
    """Exports cleaned and matched transaction information to a csv file

    Args:
        payments: (list[Transaction]) A list of transactions to export
        filename: (str) The name of exported file

    Returns:
        None
    """
    fieldnames = ["Date", "Site", "Name", "Amount"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in payments:
            writer.writerow(transaction.toDict())


def exportWordsToIgnore(words: list[str]) -> None:
    """Exports a list of words to ignore to a csv file

    Args:
        words: A list of words to ignore

    Returns:
        None
    """
    with open("WordsToIgnore.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])
        for word in words:
            writer.writerow([word])


def export_balances(balances: list[Balance]) -> None:
    fieldnames = [
        "Site",
        "Annual Fee",
        "Remaining from this FY",
        "Outstanding from previous FYs",
        "Pay Frequency",
    ]
    with open("Balances.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for balance in balances:
            writer.writerow(balance.to_dict())
