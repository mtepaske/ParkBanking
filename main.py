import argparse
import datetime as dt
import shutil
import sys
from typing import TypedDict
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from account import Account
from balance import Balance
from database import (
    DB_PATH,
    AccountRepository,
    BalanceRepository,
    IgnoreRepository,
    connect,
    disconnect,
    initialise_database,
)
from files import (
    export_accounts,
    export_balances,
    export_payments,
    import_accounts,
    import_balances,
    import_matched,
    import_payments,
    import_words_to_ignore,
)
from match import Matcher
from transactions import Transaction
from user import get_input


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
        try:
            choice = int(get_input("Choose an action"))
            name, action = available_actions[choice - 1]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please choose from list")
    return action["function"](test)


def load_from_db(
    account_repo: AccountRepository,
    balance_repo: BalanceRepository,
    ignore_repo: IgnoreRepository,
) -> tuple[list[Account], list[Balance], list[str]]:
    """Load data from a database

    Args:
        account_repo: (AccountRepository) The account repository
        balance_repo: (BalanceRepository) The balance repository
        ignore_repo: (IgnoreRepository) The ignore repository

    Returns:
        (tuple[list[Account], list[Balance], list[str]]) A tuple containing the information loaded from the database
    """
    accounts = account_repo.get_active()
    balances = balance_repo.get_active()
    for account in accounts:
        for balance in balances:
            if account.id == balance.account_id:
                account.add_balance(balance)
                break
        if account.balance is None:
            print(
                f"Could not find matching balance for {account}\nAssigning default balance"
            )
            balance = Balance(account.id, account.site, "7550", "7550", "0", "m")
            balances.append(balance)
            account.add_balance(balance)
    ignore = ignore_repo.get_all()
    if len(ignore) == 0:
        print("Ignore Repository is Empty. Importing From CSV")
        ignore = import_words_to_ignore("WordsToIgnore.csv")
    print("Accounts loaded")
    return (accounts, balances, ignore)


def load_from_db_action(test: bool = False) -> None:
    """Helper action to call load_from_db

    Args:
        test: (bool) True when in test mode, False otherwise
    Returns:
        None
    """
    account_repo = repos["account_repo"]
    balance_repo = repos["balance_repo"]
    ignore_repo = repos["ignore_repo"]
    assert account_repo is not None
    assert balance_repo is not None
    assert ignore_repo is not None
    state["accounts"], state["balances"], state["words_to_ignore"] = load_from_db(
        account_repo, balance_repo, ignore_repo
    )
    actions["Import Accounts & Balances From CSV"]["available"] = False
    actions["Load Accounts From Database"]["available"] = False
    actions["View Accounts"]["available"] = True
    actions["Import Previously Matched Transactions"]["available"] = True
    actions["Export Accounts To CSV"]["available"] = True
    actions["Save To Database"]["available"] = True
    if state["transactions"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def save_to_db(
    accounts: list[Account],
    balances: list[Balance],
    ignore: list[str],
    account_repo: AccountRepository,
    balance_repo: BalanceRepository,
    ignore_repo: IgnoreRepository,
) -> None:
    """Save loaded data into the repository

    Args:
        accounts: (list[Account]) A list of loaded accounts
        balances: (list[Balance]) A list of loaded balances
        ignore: (list[str]) A list of loaded words to ignore
        account_repo: (AccountRepository) The account repository
        balance_repo: (BalanceRepository) The balance repository
        ignore_repo: (IgnoreRepository) The ignore repository
    Returns:
        None
    """
    account_repo.insert_all(accounts)
    balance_repo.insert_all(balances)
    ignore_repo.replace_all(ignore)


def save_to_db_action(test: bool = False) -> None:
    """Helper action to call save_to_db

    Args:
        test: (bool) True when in test mode, False otherwise
    Returns:
        None
    """
    accounts = state["accounts"]
    balances = state["balances"]
    ignore = state["words_to_ignore"]
    account_repo = repos["account_repo"]
    balance_repo = repos["balance_repo"]
    ignore_repo = repos["ignore_repo"]
    assert accounts is not None
    assert balances is not None
    assert ignore is not None
    assert account_repo is not None
    assert balance_repo is not None
    assert ignore_repo is not None
    save_to_db(accounts, balances, ignore, account_repo, balance_repo, ignore_repo)
    actions["Save To Database"]["available"] = False


def import_accounts_from_csv() -> tuple[list[Account], list[Balance]]:
    """Imports accounts and balances files

    Returns:
        (tuple[list[Account], list[Balances]]) A tuple containing imported accounts and imported balances

    Raises:
        ValueError: If the accounts and balances are different sizes, or if the site numbers dot match
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
    actions["Import Accounts & Balances From CSV"]["available"] = False
    actions["Load Accounts From Database"]["available"] = False
    actions["View Accounts"]["available"] = True
    actions["Import Previously Matched Transactions"]["available"] = True
    actions["Save To Database"]["available"] = True
    actions["Export Accounts To CSV"]["available"] = True
    if state["transactions"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def show_accounts(accounts: list[Account]):
    print("ACCOUNTS")
    Matcher.print_accounts(accounts)
    print("[b] -> Back")
    while True:
        try:
            choice = input("Which Account? ")
            if choice == "b":
                print("Back")
                return
            else:
                account = accounts[int(choice) - 1]
                break
        except ValueError:
            print("Choice must be a number")
        except IndexError:
            print("Choice must be a valid index")
    print(f"You have picked {account}")
    edit_account(account)


def show_accounts_action(test: bool = False):
    assert state["accounts"] is not None
    show_accounts(state["accounts"])


def edit_account(account: Account):
    if account.balance is not None:
        balance = account.balance
        attributes = {
            "Site Number": {"value": account.site, "function": account.change_site},
            "Name": {"value": account.name, "function": account.change_name},
            "Annual Fees": {"value": balance.annual, "function": balance.change_annual},
            "Remaining Fees": {
                "value": balance.remaining,
                "function": balance.change_remaining,
            },
            "Outstanding Fees": {
                "value": balance.outstanding,
                "function": balance.change_outstanding,
            },
            "Pay Frequency": {
                "value": balance.pay_frequency,
                "function": balance.change_payfrequency,
            },
            "Active": {"value": account.active, "function": account.switch_active},
        }
    else:
        attributes = {
            "Site Number": {"value": account.site, "function": account.change_site},
            "Name": {"value": account.name, "function": account.change_name},
            "Active": {"value": account.active, "function": account.switch_active},
        }
    print(f"Editing Account: {account.site}, {account.name}")
    while True:
        editable = [(name, action) for name, action in attributes.items()]
        for i, (name, action) in enumerate(editable, start=1):
            print(f"[{i}] - {name}: {action['value']}")
        print("[b] - Back")
        try:
            choice = input("What would you like to change?")
            if choice == "b":
                print("Back")
                return
            else:
                name, action = editable[int(choice) - 1]
                break
        except (ValueError, IndexError):
            print("Invalid choice. Please choose from list")
    return action["function"]()


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


def import_banking_action(test: bool = False) -> None:
    """Helper function to call import_banking

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    state["transactions"] = import_banking(test)
    actions["Import Banking Data"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = False
    if state["accounts"] is not None and state["balances"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def import_mached_transactions(filepath: str, test: bool = False):
    accounts = state["accounts"]
    assert accounts is not None
    if test:
        transactions = import_matched("test_matched.csv", accounts)
    else:
        try:
            transactions = import_matched(filepath, accounts)
        except FileNotFoundError:
            print("Filepath not valid")
            return
    return transactions


def import_mached_transactions_action(test: bool = False):
    filepath = get_input(
        "Whats the name of the file containing matched transaction information?"
    )
    state["transactions"] = import_mached_transactions(filepath, test)
    actions["Import Banking Data"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Export Transactions to CSV"]["available"] = True


def match_transactions(
    accounts: list[Account], transactions: list[Transaction], ignore: list[str]
) -> Matcher:
    """Matches transactions to accounts using the Matcher class

    Args:
        accounts: (list[Account]) A list of accounts to match to
        transactions: (list[Transaction]) A list of transactions to match

    Returns:
        (tuple[list[str], Matcher]) A tuple containing a list of words to ignore, and the instance of the matcher class
    """
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keyword_match(transaction)
        matcher.match(transaction, possibilities)
    review_matches(matcher, transactions, accounts)
    return matcher


def match_transactions_action(test: bool = False) -> None:
    """Helper function to call match_transactions

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None

    Raises:
        FileNotFoundError: If no file containing words to ignore can be found
    """
    accounts = state["accounts"]
    balances = state["balances"]
    transactions = state["transactions"]
    ignore = state["words_to_ignore"]
    if ignore is None:
        ignore_repo = repos["ignore_repo"]
        assert ignore_repo is not None
        ignore = ignore_repo.get_all()
        if len(ignore) == 0:
            print("Words to Ignore Empty. Importing from CSV")
            ignore = import_words_to_ignore("WordsToIgnore.csv")
    assert accounts is not None
    assert balances is not None
    assert transactions is not None
    assert ignore is not None
    state["matcher"] = match_transactions(accounts, transactions, ignore)
    actions["Match Transactions to Accounts"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Proccess Unknown Words"]["available"] = True
    actions["Export Transactions to CSV"]["available"] = True


def review_matches(
    matcher: Matcher, transactions: list[Transaction], accounts: list[Account]
) -> None:
    """Prints a list of matched transactions and the matched accounts for proofing

    Returns:
        None
    """
    index = 1
    while True:
        for transaction in transactions:
            account = transaction.account
            assert account is not None
            print(
                f"{account.site}: {account.name} -> {transaction.amount} - {transaction.details}"
            )
            index += 1
        while True:
            choice = input("Are all the transactions matched correctly?: (y/n)")
            if choice == "y":
                print("Transactions matched successfully")
                return
            elif choice == "n":
                while True:
                    match_to_change = int(input("Which match?: "))
                    try:
                        transaction_to_change = transactions[match_to_change - 1]
                        matcher.change_match(transaction_to_change, accounts)
                        break
                    except (IndexError, KeyError):
                        print("Must choose from the available indexes")
            else:
                print("Please choose y or n")


def process_payments(transactions: list[Transaction]) -> None:
    """Procces the matched transactions and update account balances

    Args:
        transactions: (list[Transaction]) A list of the matched transactions

    Returns:
        None

    Raises:
        ValueError: If a transaction hasn't been matched or if an account has no balance instance
    """
    for transaction in transactions:
        assert transaction.account is not None
        assert transaction.account.balance is not None
        transaction.account.balance.add_payment(transaction.amount)


def process_payments_action(test: bool = False) -> None:
    """Helper function to call process_payments

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    transactions = state["transactions"]
    assert transactions is not None
    process_payments(transactions)
    actions["Proccess Payments"]["available"] = False


def procces_unknown_words(matcher: Matcher) -> list[str]:
    """Proccess any unknown words from the matching process

    Args:
        matcher: (Matcher) The instance of the Matcher classes used

    Returns:
        None
    """
    matcher.unknown_words()
    ignore = matcher.ignore
    return ignore


def procces_unknown_words_action(test: bool = False) -> None:
    """Helper function to call procces_unknown_words

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    matcher = state["matcher"]
    assert matcher is not None
    state["words_to_ignore"] = procces_unknown_words(matcher)
    actions["Proccess Unknown Words"]["available"] = False


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


def export_accounts_to_csv_action(test: bool = False):
    """Helper function to call export_accounts_to_csv

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    accounts = state["accounts"]
    balances = state["balances"]
    assert accounts is not None
    assert balances is not None
    export_accounts_to_csv(accounts, balances, test)


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


def export_transactions_to_csv_action(test: bool = False):
    """Helper function to call export_transactions_to_csv

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    transactions = state["transactions"]
    assert transactions is not None
    export_transactions_to_csv(transactions, test)


def exit_program(test: bool = False) -> None:
    """Exits the program

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
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
    "View Accounts": {"available": False, "function": show_accounts_action},
    "Import Banking Data": {"available": True, "function": import_banking_action},
    "Import Previously Matched Transactions": {
        "available": False,
        "function": import_mached_transactions_action,
    },
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
        "available": False,
        "function": export_transactions_to_csv_action,
    },
    "Save To Database": {"available": False, "function": save_to_db_action},
    "Export Accounts To CSV": {
        "available": False,
        "function": export_accounts_to_csv_action,
    },
    "Exit Program": {"available": True, "function": exit_program},
}

if __name__ == "__main__":

    args = start_program()
    db_path = DB_PATH.with_name("parkbanking_test.db") if args.test else DB_PATH
    connection = connect(db_path)
    try:
        initialise_database(connection)
        repos["account_repo"] = AccountRepository(connection)
        repos["balance_repo"] = BalanceRepository(connection)
        repos["ignore_repo"] = IgnoreRepository(connection)
        while True:
            show_menu(args.test)
    finally:
        disconnect(connection)
