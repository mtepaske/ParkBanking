import sys

from rich.console import Console
from rich.table import Table

from application import Application
from cli.accounts_menu import accounts_menu
from cli.export_menu import export_menu
from cli.import_menu import import_menu
from cli.matching import match_to_account, unknown_words
from cli.settings_menu import settings_menu
from services.imports import (
    import_words_to_ignore,
)
from services.match import Matcher, match_transactions, review_payment
from services.settings import get_setting


def start_program(app: Application) -> None:
    business_name = get_setting("business_name")
    print(f"\nPAYMENT TRACKING FOR {business_name}")
    if get_setting("auto_load_from_db") == "True":
        load_from_db(app=app)
        actions["Load From Database"]["available"] = False


def determine_available(app: Application) -> list[tuple]:
    if len(app.state.accounts) > 0 and len(app.state.transactions) > 0:
        for transaction in app.state.transactions:
            if transaction.account is None:
                actions["Match Transactions to Accounts"]["available"] = True
            else:
                actions["Proccess Payments"]["available"] = True
    else:
        actions["Match Transactions to Accounts"]["available"] = False
        actions["Proccess Payments"]["available"] = False
    return [(name, action) for name, action in actions.items() if action["available"]]


def show_menu(app: Application) -> None:
    print("\nMAIN MENU")
    availables = determine_available(app=app)
    for i, (name, action) in enumerate(availables, start=1):
        print(f"[{i}] -> {name}")
    while True:
        try:
            choice = int(input("Choose an Action: "))
            name, action = availables[choice - 1]
            break
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")
    return action["function"](app=app)


def exit_program(app: Application) -> None:
    business_name = get_setting("business_name")
    if get_setting("auto_save_to_db") == "True":
        save_all_to_db(app=app)
    print(f"\nEXITING PAYMENT TRACKING FOR {business_name}")
    sys.exit(0)


def load_from_db(app: Application) -> None:
    print("\nLOADING DATA FROM DATABASE")
    app.state.accounts = app.repos.account_repo.get_active_accounts()
    print("Accounts Loaded From Database")
    app.state.words_to_ignore = app.repos.ignore_repo.get_all_ignore()
    if len(app.state.words_to_ignore) == 0:
        print("No Words to Ignore in Database\nAttempting to Import From File")
        try:
            app.state.words_to_ignore = import_words_to_ignore("WordsToIgnore")
        except FileNotFoundError:
            print(
                "No File Named WordsToIgnore.csv Found\nLoading With No Words to Ignore"
            )
        print("Words to Ignore Imported")
    else:
        print("Words to Ignore Loaded from Database")


def save_all_to_db(app: Application) -> None:
    print("\nSAVING TO DATABASE")
    accounts = app.state.accounts
    ignore = app.state.words_to_ignore
    payments = app.state.payments
    count = app.repos.account_repo.save_accounts(accounts)
    print(
        f"Accounts & Balances Saved\n{count['Inserted']} New Accounts Instered - {count['Updated']} Accounts Updated"
    )
    app.repos.ignore_repo.replace_all_ignore(ignore)
    app.repos.account_repo.save_payments(payments)
    print("Words to Ignore Saved")


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
    actions["Proccess Unknown Words"]["available"] = True


def process_payments(app: Application) -> None:
    print("\nPROCCESSING PAYMENTS")
    transactions = app.state.transactions
    unproccessed = []
    console = Console()
    table = Table(show_lines=True)
    table.add_column("Site Holder")
    table.add_column("Site Number")
    table.add_column("Remaining")
    table.add_column("Outstanding")
    table.add_column("Credit")
    table.add_column("->", justify="center")
    table.add_column("New Remaining")
    table.add_column("New Outstanding")
    table.add_column("New Credit")
    for transaction in transactions:
        if transaction.account is not None:
            assert transaction.account.balance is not None
            old, new = review_payment(transaction.account.balance, transaction.amount)
            rem_col = "red" if old["Remaining"] == new["Remaining"] else "green"
            out_col = "red" if old["Outstanding"] == new["Outstanding"] else "green"
            cre_col = "red" if old["Credit"] == new["Credit"] else "green"
            table.add_row(
                f"[blue]{transaction.account.name}[/blue]",
                f"[blue]{transaction.account.site_number}[/blue]",
                f"${old['Remaining']:,.2f}",
                f"${old['Outstanding']:,.2f}",
                f'${old["Credit"]:,.2f}',
                f"[blue]-${transaction.amount:,.2f}[/blue]",
                f"[{rem_col}]${new['Remaining']:,.2f}[/{rem_col}]",
                f"[{out_col}]${new['Outstanding']:,.2f}[/{out_col}]",
                f"[{cre_col}]${new['Credit']:,.2f}[/{cre_col}]",
            )
            transaction.account.balance.add_payment(transaction.amount)
            app.state.payments.append(transaction)
        else:
            unproccessed.append(transaction)
    app.state.transactions = unproccessed
    console.print(table)
    print("Balances Updated")


def procces_unknown_words(app: Application) -> None:
    print("\nPROCCESSING UNKNOWN WORDS")
    accounts = app.state.accounts
    unknown = app.state.unknown_words
    ignore = app.state.words_to_ignore
    unknown_words(accounts, unknown, ignore)
    print("Unknown Words Proccessed")
    actions["Proccess Unknown Words"]["available"] = False


actions = {
    "Accounts Menu": {"available": True, "function": accounts_menu},
    "Match Transactions to Accounts": {
        "available": False,
        "function": match,
    },
    "Proccess Payments": {"available": False, "function": process_payments},
    "Proccess Unknown Words": {
        "available": False,
        "function": procces_unknown_words,
    },
    "Load From Database": {
        "available": True,
        "function": load_from_db,
    },
    "Save To Database": {"available": True, "function": save_all_to_db},
    "Import Menu": {
        "available": True,
        "function": import_menu,
    },
    "Export Menu": {
        "available": True,
        "function": export_menu,
    },
    "Settings Menu": {"available": True, "function": settings_menu},
    "Exit Program": {"available": True, "function": exit_program},
}
