import sys

from application import Application
from cli.accounts_menu import accounts_menu
from cli.export_menu import export_menu
from cli.matching import match_to_account, unknown_words
from services.imports import (
    import_account_info_from_csv,
    import_matched,
    import_payments,
    import_words_to_ignore,
)
from services.match import Matcher, apply_payments, match_transactions


def show_menu(app: Application) -> None:
    print("\nMAIN MENU")
    availables = [
        (name, action) for name, action in actions.items() if action["available"]
    ]
    for i, (name, action) in enumerate(availables, start=1):
        print(f"{i} -> {name}")
    while True:
        try:
            choice = int(input("Choose an Action: "))
            name, action = availables[choice - 1]
            break
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")
    return action["function"](app=app)


def exit_program(app: Application) -> None:
    print("\nEXITING PROGRAM")
    sys.exit(0)


def load_from_db(app: Application) -> None:
    print("\nLOADING DATA FROM DATABASE")
    app.state.accounts = app.repos.account_repo.get_active_accounts()
    print("Accounts Loaded From Database")
    app.state.words_to_ignore = app.repos.ignore_repo.get_all_ignore()
    if len(app.state.words_to_ignore) == 0:
        print("No Words to Ignore in Database\nAttempting to Import From File")
        try:
            app.state.words_to_ignore = import_words_to_ignore()
        except FileNotFoundError:
            print(
                "No File Named WordsToIgnore.csv Found\nLoading With No Words to Ignore"
            )
        print("Words to Ignore Imported")
    else:
        print("Words to Ignore Loaded from Database")
    actions["Import Accounts & Balances From CSV"]["available"] = False
    actions["Load From Database"]["available"] = False
    actions["Accounts Menu"]["available"] = True
    actions["Import Previously Matched Transactions"]["available"] = True
    if len(app.state.transactions) != 0:
        actions["Match Transactions to Accounts"]["available"] = True


def save_all_to_db(app: Application) -> None:
    print("\nSAVING TO DATABASE")
    accounts = app.state.accounts
    ignore = app.state.words_to_ignore
    app.repos.account_repo.save_accounts(accounts)
    print("Accounts & Balances Saved")
    app.repos.ignore_repo.replace_all_ignore(ignore)
    print("Words to Ignore Saved")


def import_accounts_from_csv(app: Application) -> None:
    print("\nIMPORTING ACCOUNTS INFORMATION")
    print("[b] -> Back")
    print("[d] -> Default Filepath (files/Accounts.csv)")
    accounts_filepath = input("Enter Filepath for Accounts: ")
    if accounts_filepath == "b":
        print("BACK")
        return
    elif accounts_filepath == "d":
        accounts_filepath = "files/Accounts.csv"
    print("[b] -> Back")
    print("[d] -> Default Filepath (files/Balances.csv)")
    balances_filepath = input("Enter Filepath for Balances: ")
    if balances_filepath == "b":
        print("BACK")
        return
    elif balances_filepath == "d":
        balances_filepath = "files/Balances.csv"
    try:
        app.state.accounts = import_account_info_from_csv(accounts_filepath)
        print("Accounts Information Imported")
    except FileNotFoundError:
        print(
            f"One or Both Files Named {accounts_filepath} & {balances_filepath} Not Found"
        )
        return
    actions["Import Accounts & Balances From CSV"]["available"] = False
    actions["Load From Database"]["available"] = False
    actions["Accounts Menu"]["available"] = True
    actions["Import Previously Matched Transactions"]["available"] = True
    if app.state.transactions is not None:
        actions["Match Transactions to Accounts"]["available"] = True


def import_banking(app: Application) -> None:
    print("\nIMPORTING BANKING DATA")
    print("[b] -> Back")
    print("[d] -> Default Filepath (files/Transactions.csv)")
    filepath = input("Enter Filepath: ")
    if filepath == "b":
        print("BACK")
        return
    elif filepath == "d":
        app.state.transactions = import_payments()
        return
    try:
        app.state.transactions = import_payments(filepath)
    except FileNotFoundError:
        print(f"No File Named {filepath} Found")
    print("Banking Data Imported")
    actions["Import Banking Data"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = False
    if len(app.state.accounts) != 0:
        actions["Match Transactions to Accounts"]["available"] = True


def import_mached_transactions(app: Application):
    print("\nIMPORTING MATCHED TRANSACTIONS")
    accounts = app.state.accounts
    filepath = input("Enter Filepath: ")
    while True:
        try:
            transactions = import_matched(filepath, accounts)
            app.state.transactions = transactions
            break
        except FileNotFoundError:
            print(f"No File Named {filepath} Found")
    print("Matched Transactions Imported")
    actions["Import Banking Data"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = False
    actions["Proccess Payments"]["available"] = True


def match(app: Application) -> None:
    print("\nMATCHING TRANSACTIONS")
    accounts = app.state.accounts
    transactions = app.state.transactions
    ignore = app.state.words_to_ignore
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = match_transactions(matcher, transaction)
        match_to_account(transaction, possibilities, accounts)
    app.state.unknown_words = matcher.get_unknown_words()
    print("Transactions Matched")
    actions["Match Transactions to Accounts"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Proccess Unknown Words"]["available"] = True


def process_payments(app: Application) -> None:
    print("\nPROCCESSING PAYMENTS")
    transactions = app.state.transactions
    apply_payments(transactions)
    print("Balances Updated")
    actions["Proccess Payments"]["available"] = False
    actions["Import Previously Matched Transactions"]["available"] = True


def procces_unknown_words(app: Application) -> None:
    print("\nPROCCESSING UNKNOWN WORDS")
    accounts = app.state.accounts
    unknown = app.state.unknown_words
    ignore = app.state.words_to_ignore
    unknown_words(accounts, unknown, ignore)
    print("Unknown Words Proccessed")
    actions["Proccess Unknown Words"]["available"] = False


actions = {
    "Load From Database": {
        "available": True,
        "function": load_from_db,
    },
    "Accounts Menu": {"available": False, "function": accounts_menu},
    "Import Accounts & Balances From CSV": {
        "available": True,
        "function": import_accounts_from_csv,
    },
    "Import Banking Data": {"available": True, "function": import_banking},
    "Import Previously Matched Transactions": {
        "available": False,
        "function": import_mached_transactions,
    },
    "Export Menu": {
        "available": True,
        "function": export_menu,
    },
    "Match Transactions to Accounts": {
        "available": False,
        "function": match,
    },
    "Proccess Payments": {"available": False, "function": apply_payments},
    "Proccess Unknown Words": {
        "available": False,
        "function": procces_unknown_words,
    },
    "Save To Database": {"available": True, "function": save_all_to_db},
    "Exit Program": {"available": True, "function": exit_program},
}
