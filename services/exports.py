import csv
import datetime as dt
import shutil
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction


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


def export_accounts_to_csv(
    accounts: list[Account], balances: list[Balance], test: bool = False
):
    """Export loaded data into a csv file

    Args:
        accounts: (list[Account]) The loaded account data
        balances: (list[Balances]) The loaded balance data
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
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
    """Exports matched transactions to a csv file

    Args:
        transactions: (list[Transaction] | None) A list of loaded transactions
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    if test:
        test_flag = "test_"
    else:
        test_flag = ""
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    source_file = "test.csv" if test else "Transactions.csv"
    shutil.copy2(source_file, f"{test_flag}{last_month}{last_month_year}Raw.csv")
    export_payments(transactions, f"{test_flag}{last_month} {last_month_year}.csv")
    print(f"Matched payments saved as {last_month} {last_month_year}.csv")
