import csv

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction
from services.settings import APP_DIRECTORY, get_setting

export_folder = APP_DIRECTORY / get_setting("exports_folder")
export_folder.mkdir(parents=True, exist_ok=True)


def export_accounts_to_csv(accounts: list[Account], filename: str) -> None:
    fieldnames = ["ID", "Active", "Name", "Site", "Aliases"]
    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            writer.writerow(account.to_dict())


def export_balances_to_csv(balances: list[Balance], filename: str) -> None:
    fieldnames = [
        "Site",
        "ID",
        "Account ID",
        "Annual Fee",
        "Remaining from this FY",
        "Outstanding from previous FYs",
        "Pay Frequency",
    ]
    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for balance in balances:
            writer.writerow(balance.to_dict())


def export_payments_to_csv(payments: list[Transaction], filename: str) -> None:
    fieldnames = ["Date", "Site", "Name", "Amount"]
    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in payments:
            writer.writerow(transaction.to_dict())


def export_ignore_to_csv(words: list[str], filename: str) -> None:
    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])
        for word in words:
            writer.writerow([word])
