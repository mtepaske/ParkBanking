import csv
from decimal import Decimal

from cli.matching import review_matches
from models.account import Account
from models.balance import Balance
from models.transactions import Transaction


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


def import_accounts_from_csv() -> tuple[list[Account], list[Balance]]:
    """Imports accounts and balances files

    Returns:
        (tuple[list[Account], list[Balances]]) A tuple containing imported accounts and imported balances
    """
    # Importing csvs should update database not overwrite it.
    accounts = import_accounts("Accounts.csv")
    balances = import_balances("Balances.csv")
    print("Imported Accounts and Balances")
    for account in accounts:
        for balance in balances:
            if account.site == balance.site:
                account.add_balance(balance)
                break
        if account.balance is None:
            print(
                f"Could not find matching balance for {account}\nAssigning default balance"
            )
            balance = Balance(account.id, account.site, "7550", "7550", "0", "m")
            balances.append(balance)
            account.add_balance(balance)
    print("Accounts loaded")
    return (accounts, balances)


def import_banking(test: bool = False) -> list[Transaction]:
    """Import banking raw banking information

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        (list[Transaction]) A list of all the relavent transactions
    """
    if test:
        transactions = import_payments("test.csv")
    else:
        transactions = import_payments("Transactions.csv")
    print("Imported Transactions")
    return transactions


def import_mached_transactions(
    filepath: str, accounts: list[Account], test: bool = False
) -> list[Transaction] | None:
    """Imports a csv file containing previously matched transactions

    Args:
        filepath: (str) The path of the file
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    assert accounts is not None
    if test:
        transactions = import_matched("test_matched.csv", accounts)
    else:
        try:
            transactions = import_matched(filepath, accounts)
        except FileNotFoundError:
            print("Filepath not valid")
            return
    review_matches(transactions, accounts)
    return transactions
