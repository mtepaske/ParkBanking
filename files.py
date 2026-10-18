import csv
from decimal import Decimal

from account import Account
from balance import Balance
from transactions import Transaction


def import_payments(filepath: str) -> list[Transaction]:
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
            if row["Transaction Details"] == "CASH":
                continue
            transactions.append(Transaction.from_csv(row))
    return transactions


def import_accounts(filepath: str) -> list[Account]:
    """Import a csv containing account information as Account classes

    Args:
        filepath: (str) The name of the file to import

    Returns:
        (list[Account]) A list of imported accounts
    """
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [Account.from_csv(row) for row in reader]


def import_words_to_ignore(filepath: str) -> list[str]:
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
    """Imports a csv containing balance information

    Args:
        filepath: (str) The name of the file to import

    Returns:
        (list[Balance]) A list of balances
    """
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [Balance.from_csv(row) for row in reader]


def import_matched(filepath: str, accounts: list[Account]) -> list[Transaction]:
    with open(filepath, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [Transaction.from_matched(row, accounts) for row in reader]


def export_accounts(accounts: list[Account], filepath: str) -> None:
    """Export updated account information as a csv file

    Args:
        accounts: (list[Account]) A list of accounts to export

    Returns:
        None
    """
    fieldnames = ["ID", "Active", "Name", "Site", "Aliases"]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            writer.writerow(account.to_dict())


def export_payments(payments: list[Transaction], filepath: str) -> None:
    """Exports cleaned and matched transaction information to a csv file

    Args:
        payments: (list[Transaction]) A list of transactions to export
        filename: (str) The name of exported file

    Returns:
        None
    """
    fieldnames = ["Date", "Site", "Name", "Amount"]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in payments:
            writer.writerow(transaction.to_dict())


def export_words_to_ignore(words: list[str], filepath: str) -> None:
    """Exports a list of words to ignore to a csv file

    Args:
        words: (list[str]) A list of words to ignore

    Returns:
        None
    """
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])
        for word in words:
            writer.writerow([word])


def export_balances(balances: list[Balance], filepath: str) -> None:
    fieldnames = [
        "Site",
        "ID",
        "Account ID",
        "Annual Fee",
        "Remaining from this FY",
        "Outstanding from previous FYs",
        "Pay Frequency",
    ]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for balance in balances:
            writer.writerow(balance.to_dict())
