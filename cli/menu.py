import sys

from application import Application
from cli.accounts import show_accounts
from cli.menu import get_input
from services.exports import export_accounts_to_csv, export_transactions_to_csv
from services.imports import (
    import_accounts_from_csv,
    import_banking,
    import_mached_transactions,
    import_words_to_ignore,
)
from services.transactions import (
    match_transactions,
    procces_unknown_words,
    process_payments,
)


def get_input(question: str) -> str:
    """Prompts the user for input

    Args:
        question: (str) The statement to print

    Returns:
        (str) The user input
    """
    return input(f"{question}: ")


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


def exit_program(test: bool = False) -> None:
    """Exits the program

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    print("Exiting Program")
    sys.exit(0)


def load_from_db_action(app: Application, test: bool = False) -> None:
    """Helper action to call load_from_db

    Args:
        test: (bool) True when in test mode, False otherwise
    Returns:
        None
    """
    app.load_from_db()
    actions["Import Accounts & Balances From CSV"]["available"] = False
    actions["Load Accounts From Database"]["available"] = False
    actions["View Accounts"]["available"] = True
    actions["Import Previously Matched Transactions"]["available"] = True
    actions["Export Accounts To CSV"]["available"] = True
    actions["Save To Database"]["available"] = True
    if app.state.transactions is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def save_to_db_action(app: Application, test: bool = False) -> None:
    """Helper action to call save_to_db

    Args:
        test: (bool) True when in test mode, False otherwise
    Returns:
        None
    """
    app.save_to_db()
    actions["Save To Database"]["available"] = False


def import_accounts_from_csv_action(app: Application, test: bool = False) -> None:
    """Helper function to call import_accounts_and_balances

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    acts_and_bal = import_accounts_from_csv()
    app.state.accounts = acts_and_bal[0]
    app.state.balances = acts_and_bal[1]
    actions["Import Accounts & Balances From CSV"]["available"] = False
    actions["Load Accounts From Database"]["available"] = False
    actions["View Accounts"]["available"] = True
    actions["Import Previously Matched Transactions"]["available"] = True
    actions["Save To Database"]["available"] = True
    actions["Export Accounts To CSV"]["available"] = True
    if app.state.transactions is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def show_accounts_action(app: Application, test: bool = False) -> None:
    """Helper function to call show_accounts

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    show_accounts(app.state.accounts, app.state.balances)


def import_banking_action(app: Application, test: bool = False) -> None:
    """Helper function to call import_banking

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    app.state.transactions = import_banking(test)
    actions["Import Banking Data"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = False
    if app.state.accounts is not None and app.state.balances is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def import_mached_transactions_action(app: Application, test: bool = False):
    """Helper action to call import_mached_transactions

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    accounts = app.state.accounts
    while True:
        filepath = get_input(
            "Whats the name of the file containing matched transaction information?"
        )
        transactions = import_mached_transactions(filepath, accounts, test)
        if transactions is not None:
            app.state.transactions = transactions
            break
    actions["Import Banking Data"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Export Transactions to CSV"]["available"] = True


def match_transactions_action(app: Application, test: bool = False) -> None:
    """Helper function to call match_transactions

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    accounts = app.state.accounts
    balances = app.state.balances
    transactions = app.state.transactions
    ignore = app.state.words_to_ignore
    if ignore is None:
        ignore_repo = app.repos.ignore_repo
        assert ignore_repo is not None
        ignore = ignore_repo.get_all()
        if len(ignore) == 0:
            print("Words to Ignore Empty. Importing from CSV")
            ignore = import_words_to_ignore("WordsToIgnore.csv")
    assert accounts is not None
    assert balances is not None
    assert transactions is not None
    assert ignore is not None
    app.state.matcher = match_transactions(accounts, transactions, ignore)
    actions["Match Transactions to Accounts"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Proccess Unknown Words"]["available"] = True
    actions["Export Transactions to CSV"]["available"] = True


def process_payments_action(app: Application, test: bool = False) -> None:
    """Helper function to call process_payments

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    transactions = app.state.transactions
    process_payments(transactions)
    actions["Proccess Payments"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = True


def procces_unknown_words_action(app: Application, test: bool = False) -> None:
    """Helper function to call procces_unknown_words

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    matcher = app.state.matcher
    assert matcher is not None
    app.state.words_to_ignore = procces_unknown_words(matcher)
    actions["Proccess Unknown Words"]["available"] = False


def export_accounts_to_csv_action(app: Application, test: bool = False):
    """Helper function to call export_accounts_to_csv

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    accounts = app.state.accounts
    balances = app.state.balances
    assert accounts is not None
    assert balances is not None
    export_accounts_to_csv(accounts, balances, test)


def export_transactions_to_csv_action(app: Application, test: bool = False):
    """Helper function to call export_transactions_to_csv

    Args:
        test: (bool) True when in test mode, False otherwise

    Returns:
        None
    """
    transactions = app.state.transactions
    assert transactions is not None
    export_transactions_to_csv(transactions, test)


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
