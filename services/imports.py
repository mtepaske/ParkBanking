import csv
from decimal import Decimal

from application import APP_DIRECTORY
from models.account import Account
from models.balance import Balance
from models.transactions import Transaction
from services.settings import get_setting

import_folder = APP_DIRECTORY / get_setting("import_folder")


def import_accounts(filename: str) -> list[Account]:
    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        return [Account.from_csv(row) for row in reader]


def import_balances(filename: str) -> list[Balance]:
    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        return [Balance.from_csv(row) for row in reader]


def import_words_to_ignore(filename: str) -> list[str]:
    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        return [row["Words"] for row in reader]


def import_payments(filename: str) -> list[Transaction]:
    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:
        transactions = []
        reader = csv.DictReader(file)
        for row in reader:
            # Checks for withdrawls on the statement
            if Decimal(row["Amount"]) < 0:
                continue
            # Checks for cash deposits
            if row["Transaction Details"] == "CASH":
                continue
            transactions.append(Transaction.from_csv(row))
        return transactions


def import_matched(filename: str, accounts: list[Account]) -> list[Transaction]:
    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        return [Transaction.from_matched_csv(row, accounts) for row in reader]


def import_account_info_from_csv(
    accounts_file: str, balances_file: str
) -> list[Account]:
    accounts = import_accounts(accounts_file)
    balances = import_balances(balances_file)
    # Match accounts to balances
    for account in accounts:
        for balance in balances:
            if account.site_number == balance.site_number:
                # If the account ids do not match, raises an error
                if (
                    account.account_id is not None
                    and balance.account_id is not None
                    and account.account_id != balance.account_id
                ):
                    raise ValueError("Balance ID does not match Account ID")
                account.add_balance(balance)
                break
    return accounts
