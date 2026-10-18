import argparse
import datetime as dt
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import TypedDict
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from account import Account
from balance import Balance
from database import (
    AccountRepository,
    BalanceRepository,
    IgnoreRepository,
    initialise_database,
)
from files import (
    export_accounts,
    export_balances,
    export_payments,
    import_accounts,
    import_balances,
    import_payments,
    import_words_to_ignore,
)
from match import Matcher
from transactions import Transaction


class AppState(TypedDict):
    accounts: list[Account] | None
    balances: list[Balance] | None
    transactions: list[Transaction] | None
    words_to_ignore: list[str] | None
    matcher: Matcher | None
    payments: list[Transaction] | None


state: AppState = {
    "accounts": None,
    "balances": None,
    "transactions": None,
    "words_to_ignore": None,
    "matcher": None,
    "payments": None,
}


class AppRepos(TypedDict):
    account_repo: AccountRepository | None
    balance_repo: BalanceRepository | None
    ignore_repo: IgnoreRepository | None


repos: AppRepos = {
    "account_repo": None,
    "balance_repo": None,
    "ignore_repo": None,
}


DB_PATH = Path(__file__).resolve().parent / "parkbanking.bd"


def start_program() -> argparse.Namespace:
    """Begins the program by checking for test flags

    Returns:
        Namespace
    """
    parser = argparse.ArgumentParser(
        description="Manage Caravan Park Transactions and Accounts"
    )
    parser.add_argument("--test", action="store_true", help="Run program in test mode")
    args = parser.parse_args()
    if args.test:
        print("Starting in Test mode")
    else:
        print("Starting program")
    return args


def connect(db_path=DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA fereign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def disconnect(connection: sqlite3.Connection) -> None:
    connection.close()


def show_menu(test: bool = False) -> None:
    """Shows a menu with available actions to user

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    while True:
        available_actions = [
            (name, action) for name, action in actions.items() if action["available"]
        ]
        for i, (name, action) in enumerate(available_actions, start=1):
            print(f"{i} -> {name}")
        choice = int(input("Choose an action: "))
        try:
            name, action = available_actions[choice - 1]
            return action["function"](test)
        except IndexError:
            print("Invalid choice. Please choose from list")


def load_from_db(
    account_repo: AccountRepository,
    balance_repo: BalanceRepository,
    ignore_repo: IgnoreRepository,
) -> None:
    accounts = account_repo.get_active()
    balances = balance_repo.get_active()
    for account in accounts:
        for balance in balances:
            if account.id == balance.account_id:
                account.add_balance(balance)
                break
        if account.balance is None:
            raise ValueError(f"Could not find matching balance for {account}")
    state["words_to_ignore"] = ignore_repo.get_all()
    print("Accounts loaded")


def load_from_db_action() -> None:
    account_repo = repos["account_repo"]
    balance_repo = repos["balance_repo"]
    ignore_repo = repos["ignore_repo"]
    if account_repo is not None:
        state["accounts"] = account_repo.get_active()
    else:
        print("Account Repository Not Loaded")
    if balance_repo is not None:
        state["balances"] = balance_repo.get_active()
    else:
        print("Balance Repository Not Loaded")
    if ignore_repo is not None:
        ignore = ignore_repo.get_all()
        if len(ignore) == 0:
            print("Ignore Repository is Empty. Importing From CSV")
            try:
                ignore = import_words_to_ignore("WordsToIgnore.csv")
            except FileNotFoundError:
                print("No WordsToIgnore CSV File")
        else:
            state["words_to_ignore"] = ignore
    else:
        print("Ignore Repository Not Loaded")


def save_to_db(
    accounts: list[Account] | None,
    balances: list[Balance] | None,
    ignore: list[str] | None,
    account_repo: AccountRepository | None,
    balance_repo: BalanceRepository | None,
    ignore_repo: IgnoreRepository | None,
) -> None:
    if accounts is not None:
        if account_repo is not None:
            account_repo.insert_all(accounts)
        else:
            print("Accounts Repository Not Loaded")
    else:
        print("No Accounts Loaded")
    if balances is not None:
        if balance_repo is not None:
            balance_repo.insert_all(balances)
        else:
            print("Balance Repository Not Loaded")
    else:
        print("No Accounts Loaded")
    if ignore is not None:
        if ignore_repo is not None:
            ignore_repo.replace_all(ignore)
        else:
            print("Ignore Repository Not Loaded")
    else:
        print("No Words to Ignore Loaded")


def save_to_db_action(test: bool = False) -> None:
    accounts = state["accounts"]
    balances = state["balances"]
    ignore = state["words_to_ignore"]
    account_repo = repos["account_repo"]
    balance_repo = repos["balance_repo"]
    ignore_repo = repos["ignore_repo"]
    save_to_db(accounts, balances, ignore, account_repo, balance_repo, ignore_repo)


def import_accounts_from_csv() -> tuple[list[Account], list[Balance]]:
    """Imports accounts and balances files

    Returns:
        (tuple[list[Account], list[Balances]]) A tuple containing imported accounts and imported balances

    Raises:
        ValueError: If the accounts and balances are different sizes, or if the site numbers dot match
    """
    # Change the way importing works. Want to be able to import from csvs but not by default.
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
            raise ValueError(f"Could not find matching balance for {account}")
    print("Accounts loaded")

    actions["Import Accounts & Balances"]["available"] = False
    if state["transactions"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True
    return (accounts, balances)


def import_accounts_from_csv_action(test: bool = False) -> None:
    """Helper function to call import_accounts_and_balances

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    acts_and_bal = import_accounts_from_csv()
    state["accounts"] = acts_and_bal[0]
    state["balances"] = acts_and_bal[1]


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
    actions["Import Banking Data"]["available"] = False
    if state["accounts"] is not None and state["balances"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True
    return transactions


def import_banking_action(test: bool = False) -> None:
    """Helper function to call import_banking

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    state["transactions"] = import_banking(test)


def match_transactions(
    accounts: list[Account], transactions: list[Transaction]
) -> tuple[list[str], Matcher]:
    """Matches transactions to accounts using the Matcher class

    Args:
        accounts: (list[Account]) A list of accounts to match to
        transactions: (list[Transaction]) A list of transactions to match

    Returns:
        (tuple[list[str], Matcher]) A tuple containing a list of words to ignore, and the instance of the matcher class
    """
    ignore = import_words_to_ignore("WordsToIgnore.csv")
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keyword_match(transaction)
        matcher.match(transaction, possibilities)
    review_matches()
    actions["Match Transactions to Accounts"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Proccess Unknown Words"]["available"] = True
    return (ignore, matcher)


def match_transactions_action(test: bool = False) -> None:
    """Helper function to call match_transactions

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    if state["accounts"] is not None and state["transactions"] is not None:
        matched_info = match_transactions(state["accounts"], state["transactions"])
        state["words_to_ignore"] = matched_info[0]
        state["matcher"] = matched_info[1]
    else:
        print("Accounts and Transactions not imported")


def review_matches() -> None:
    """Prints a list of matched transactions and the matched accounts for proofing

    Returns:
        None
    """
    if state["transactions"] is None:
        print("Transactions are not imported")
        return
    for transaction in state["transactions"]:
        account = transaction.account
        if account is None:
            print("Transaction has not being matched")
            print(f"{transaction.date}, ${transaction.amount}, {transaction.details}")
            continue
        print(
            f"{account.site}: {account.name} -> {transaction.amount} - {transaction.details}"
        )
    while True:
        choice = input("Are all the transactions matched correctly?: (y/n)")
        if choice == "y":
            print("Transactions macthed successfully")
            return
        else:
            print("Transaction matching failed. Terminal failure. Exiting program")
            exit_program()


def process_payments(transactions: list[Transaction]) -> None:
    """Procces the matched transactions and update account balances

    Args:
        transactions: (list[Transaction]) A list of the matched transactions

    Raises:
        ValueError: If a transaction hasn't been matched or if an account has no balance instance
    """
    for transaction in transactions:
        if transaction.account is None:
            raise ValueError("Transaction not matched")
        elif transaction.account.balance is None:
            raise ValueError("Account has no balance")
        else:
            transaction.account.balance.add_payment(transaction.amount)
    actions["Proccess Payments"]["available"] = False


def process_payments_action(test: bool = False) -> None:
    """Helper function to call process_payments

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    if state["transactions"] is not None:
        process_payments(state["transactions"])


def procces_unknown_words(matcher: Matcher) -> None:
    """Proccess any unknown words from the matching process

    Args:
        matcher: (Matcher) The instance of the Matcher classes used

    Returns:
        None
    """
    matcher.unknown_words()
    state["words_to_ignore"] = matcher.ignore
    actions["Proccess Unknown Words"]["available"] = False


def procces_unknown_words_action(test: bool = False) -> None:
    """Helper function to call procces_unknown_words

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    if state["matcher"] is not None and state["words_to_ignore"] is not None:
        procces_unknown_words(state["matcher"])


def export_accounts_to_csv(
    accounts: list[Account] | None, balances: list[Balance] | None, test: bool = False
):
    if test:
        test_flag = "test_"
    else:
        test_flag = ""
    last_month = (
        dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(months=1)
    ).strftime("%B")
    this_year = dt.datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y")
    if accounts is not None:
        export_accounts(accounts, f"{test_flag}{last_month} {this_year} - Accounts")
        print(f"Accounts saved as {test_flag}{last_month} {this_year} - Accounts.csv")
    else:
        print("No Accounts Loaded")
    if balances is not None:
        export_balances(balances, f"{test_flag}{last_month} {this_year} - Balances")
        print(f"Balances saved as {test_flag}{last_month} {this_year} - Balances.csv")
    else:
        print("No Balances Loaded")


def export_accounts_to_csv_action(test: bool = False):
    accounts = state["accounts"]
    balances = state["balances"]
    export_accounts_to_csv(accounts, balances, test)


def export_transactions_to_csv(
    transactions: list[Transaction] | None, test: bool = False
):
    if test:
        test_flag = "test_"
    else:
        test_flag = ""
    last_month = (
        dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(months=1)
    ).strftime("%B")
    this_year = dt.datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y")
    shutil.copy2("Transactions.csv", f"{test_flag}{last_month}{this_year}Raw.csv")
    if transactions is not None:
        export_payments(transactions, f"{test_flag}{last_month} {this_year}.csv")
        print(f"Matched payments saved as {last_month} {this_year}.csv")
    else:
        print("No Transactions Loaded")


def export_transactions_to_csv_action(test: bool = False):
    transactions = state["transactions"]
    export_transactions_to_csv(transactions, test)


def exit_program(test: bool = False) -> None:
    """Exits the program

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    disconnect(connection)
    print("Exiting Program")
    sys.exit(0)


actions = {
    "Import Accounts & Balances From CSV": {
        "available": True,
        "function": import_accounts_from_csv_action,
    },
    "Load Accounts From Database": {
        "available": True,
        "function": load_from_db_action,
    },
    "Import Banking Data": {"available": True, "function": import_banking_action},
    "Match Transactions to Accounts": {
        "available": False,
        "function": match_transactions_action,
    },
    "Proccess Payments": {"available": False, "function": process_payments_action},
    "Proccess Unknown Words": {
        "available": False,
        "function": procces_unknown_words_action,
    },
    "Export Transactions to CSV": {
        "available": True,
        "function": export_transactions_to_csv_action,
    },
    "Export Accounts To CSV": {
        "available": True,
        "function": export_accounts_to_csv_action,
    },
    "Exit Program": {"available": True, "function": exit_program},
}
# Change to reflect database implimentation and new actions

if __name__ == "__main__":

    connection = connect(DB_PATH)
    initialise_database(connection)

    repos["account_repo"] = AccountRepository(connection)
    repos["balance_repo"] = BalanceRepository(connection)
    repos["ignore_repo"] = IgnoreRepository(connection)

    args = start_program()
    while True:
        show_menu(args.test)
