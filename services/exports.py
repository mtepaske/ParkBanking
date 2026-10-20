import csv

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction


def export_accounts_to_csv(accounts: list[Account], filepath: str) -> None:
    fieldnames = ["ID", "Active", "Name", "Site", "Aliases"]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            writer.writerow(account.to_dict())


def export_balances_to_csv(balances: list[Balance], filepath: str) -> None:
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


def export_payments_to_csv(payments: list[Transaction], filepath: str) -> None:
    fieldnames = ["Date", "Site", "Name", "Amount"]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in payments:
            writer.writerow(transaction.to_dict())


def export_ignore_to_csv(words: list[str], filepath: str) -> None:
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])
        for word in words:
            writer.writerow([word])
