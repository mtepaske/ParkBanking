import shutil

from application import Application
from services.date import get_str_from_date, get_today
from services.exports import (
    export_accounts_to_csv,
    export_balances_to_csv,
    export_ignore_to_csv,
    export_payments_to_csv,
)
from services.settings import APP_DIRECTORY, get_setting

# Sets the folder to export to/import from based on current settings
import_folder = APP_DIRECTORY / get_setting("imports_folder")
export_folder = APP_DIRECTORY / get_setting("exports_folder")


def export_menu(app: Application) -> None:
    """
    Displays the export menu

    Args:
        app: The instance of the application
    """

    # The available actions in the export menu
    export_actions = {
        "Export Accounts & Balances": export_accounts,
        "Export Payments": export_payments,
        "Export Words to Ignore": export_words_to_ignore,
    }

    while True:

        print("\nEXPORT MENU")
        print(f"\nDefault Export Folder: {export_folder}")

        # Displays available actions and prompts user
        available = [(name, _) for name, _ in export_actions.items()]
        for i, (name, _) in enumerate(available, start=1):
            print(f"[{i}] -> {name}")
        print("[b] -> Back")
        choice = input("Choose an Action: ")

        # Back action
        if choice == "b":
            print("BACK")
            return

        # Calls the action selected by the user
        try:
            name, _ = available[int(choice) - 1]
            export_actions[name](app=app)
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def export_accounts(app: Application) -> None:
    """
    Exports account information to a CSV file

    Args:
        app: The instance of the application
    """

    print("\nEXPORTING ACCOUNT INFORMATION")
    accounts = app.state.accounts

    # Sets balances to export
    balances = []
    for account in accounts:
        balances.append(account.balance)

    # Finds the current day for default file name
    date = get_str_from_date(get_today())

    # Prompts user for file name of accounts to export
    print("[b] -> Back")
    print(f"[d] -> Default File Name: ({date} - Accounts)")
    filename = input("Enter New File Name For Accounts: ")

    # Back action
    if filename == "b":
        print("BACK")
        return

    # Default filename
    elif filename == "d":
        filename = f"{date} - Accounts"

    # Export accounts
    export_accounts_to_csv(accounts, filename)
    print(f"Accounts saved as {filename}.csv")

    # Prompts user for file name of accounts to export
    print("[b] -> Back")
    print(f"[d] -> Default File Name: ({date} - Balances)")
    filename = input("Enter New File Name For Balances: ")

    # Back action
    if filename == "b":
        print("BACK")
        return

    # Default filename
    elif filename == "d":
        filename = f"{date} - Balances"

    # Export balances
    export_balances_to_csv(balances, filename)
    print(f"Balances saved as {filename}.csv")


def export_words_to_ignore(app: Application):
    """
    Exports words to ignore to a CSV file

    Args:
        app: The instance of the application
    """

    print("\nEXPORTING WORDS TO IGNORE")
    ignore = app.state.words_to_ignore

    # Finds the current day for default file name
    date = get_str_from_date(get_today())

    # Prompts user for file name of words to ignore to export
    print("[b] -> Back")
    print(f"[d] -> Default File Name ({date} - WordsToIgnore)")
    filename = input("Enter New File Name For WordsToIgnore: ")

    # Back action
    if filename == "b":
        print("BACK")
        return

    # Default filename
    elif filename == "d":
        filename = f"{date} - WordsToIgnore"

    # Export words to ignore
    export_ignore_to_csv(ignore, filename)
    print(f"Words to Ignore Saved As {filename}.csv")


def export_payments(app: Application):
    print("\nEXPORTING PAYMENTS")

    # Add proccessed payments and unproccessed payments to one list for export
    transactions = app.state.transactions.copy()
    transactions.extend(app.state.payments.copy())

    # Orders the transactions by date and gets the first and last for default filename
    transactions.sort(key=lambda t: t.date, reverse=True)
    first_date = transactions[-1].date
    last_date = transactions[0].date

    # Sets source file for renaming
    source_file = import_folder / "Transactions.csv"

    # Attempt to copy source file to exports folder
    try:
        print("Moving & Renaming Source File")
        shutil.copy2(
            source_file,
            APP_DIRECTORY / export_folder / f"{first_date} {last_date} Raw.csv",
        )
        print(f"{source_file} Saved as {first_date} {last_date} Raw.csv")
    except FileNotFoundError:
        print("Imported Transactions File Not Found\nCanceling Copy And Move")

    # Prompts user for file name of transactions to export
    print("[b] -> Back")
    print(f"[d] -> Default File Name: ({first_date}-{last_date} Payments)")
    filename = input("Enter New File Name: ")

    # Back action
    if filename == "b":
        print("BACK")
        return

    # Default filename
    elif filename == "d":
        filename = f"{first_date} {last_date} Payments"

    # Export transactions
    export_payments_to_csv(transactions, filename)
    print(f"Matched Payments Saved As: {filename}.csv")
