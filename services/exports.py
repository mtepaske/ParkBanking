import csv
import datetime as dt
import shutil
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction


def export_accounts(accounts: list[Account], filepath: str) -> None:
    fieldnames = ["ID", "Active", "Name", "Site", "Aliases"]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            writer.writerow(account.to_dict())


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


def export_payments(payments: list[Transaction], filepath: str) -> None:
    fieldnames = ["Date", "Site", "Name", "Amount"]
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in payments:
            writer.writerow(transaction.to_dict())


def export_words_to_ignore(words: list[str], filepath: str) -> None:
    with open(f"{filepath}.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])
        for word in words:
            writer.writerow([word])


def export_accounts_to_csv(
    accounts: list[Account], balances: list[Balance], test: bool = False
):
    if test:
        test_flag = "test_"
    else:
        test_flag = ""
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    export_accounts(accounts, f"{test_flag}{last_month} {last_month_year} - Accounts")
    print(f"Accounts saved as {test_flag}{last_month} {last_month_year} - Accounts.csv")
    export_balances(balances, f"{test_flag}{last_month} {last_month_year} - Balances")
    print(f"Balances saved as {test_flag}{last_month} {last_month_year} - Balances.csv")


def export_transactions_to_csv(transactions: list[Transaction], test: bool = False):
    if test:
        test_flag = "test_"
        source_file = "test.csv"
    else:
        test_flag = ""
        source_file = "Transactions.csv"
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    shutil.copy2(source_file, f"{test_flag}{last_month}{last_month_year}Raw.csv")
    export_payments(transactions, f"{test_flag}{last_month} {last_month_year}.csv")
    print(f"Matched payments saved as {last_month} {last_month_year}.csv")
