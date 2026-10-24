import datetime as dt
import shutil
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from application import Application
from services.exports import (
    export_accounts_to_csv,
    export_balances_to_csv,
    export_ignore_to_csv,
    export_payments_to_csv,
)
from services.settings import APP_DIRECTORY, get_setting

import_folder = APP_DIRECTORY / get_setting("imports_folder")
export_folder = APP_DIRECTORY / get_setting("exports_folder")


def export_menu(app: Application) -> None:
    print("\nEXPORT MENU")
    print(f"\nDefault Export Folder: {export_folder}")
    export_actions = {
        "Export Accounts & Balances": export_accounts,
        "Export Payments": export_payments,
        "Export Words to Ignore": export_words_to_ignore,
    }
    available = [(name, _) for name, _ in export_actions.items()]
    for i, (name, _) in enumerate(available, start=1):
        print(f"[{i}] -> {name}")
    print("[b] -> Back")
    while True:
        choice = input("Choose an Action: ")
        if choice == "b":
            print("BACK")
            return
        try:
            name, _ = available[int(choice) - 1]
            break
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")
    return export_actions[name](app=app)


def export_accounts(app: Application) -> None:
    print("\nEXPORTING ACCOUNT INFORMATION")
    accounts = app.state.accounts
    balances = []
    for account in accounts:
        balances.append(account.balance)
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    print(f"[d] -> Default File Name: ({last_month} {last_month_year} - Accounts)")
    filename = input("Enter New File Name For Accounts: ")
    if filename == "d":
        filename = f"{last_month} {last_month_year} - Accounts"
    export_accounts_to_csv(accounts, filename)
    print(f"Accounts saved as {filename}.csv")
    print(f"[d] -> Default File Name: ({last_month} {last_month_year} - Balances)")
    filename = input("Enter New File Name For Balances: ")
    if filename == "d":
        filename = f"{last_month} {last_month_year} - Balances"
    export_balances_to_csv(balances, filename)
    print(f"Balances saved as {filename}.csv")


def export_payments(app: Application):
    print("\nEXPORTING PAYMENTS")
    transactions = app.state.transactions
    source_file = import_folder / "Transactions.csv"
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    try:
        print("Moving & Renaming Source File")
        shutil.copy2(
            source_file,
            APP_DIRECTORY / export_folder / f"{last_month} {last_month_year} Raw.csv",
        )
        print(f"{source_file} Saved as {last_month} {last_month_year} Raw.csv")
    except FileNotFoundError:
        print("Imported Transactions File Not Found\nCanceling Copy And Move")
    print(f"[d] -> Default File Name: ({last_month} {last_month_year} - Payments)")
    filename = input("Enter New File Name: ")
    if filename == "d":
        filename = f"{last_month} {last_month_year} Payments"
    export_payments_to_csv(transactions, filename)
    print(f"Matched Payments Saved As: {filename}.csv")


def export_words_to_ignore(app: Application):
    print("\nEXPORTING WORDS TO IGNORE")
    ignore = app.state.words_to_ignore
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    print(f"[d] -> Default File Name ({last_month} {last_month_year} - WordsToIgnore)")
    filename = input("Enter New File Name For WordsToIgnore: ")
    if filename == "d":
        filename = f"{last_month} {last_month_year} - WordsToIgnore"
    export_ignore_to_csv(ignore, filename)
    print(f"Words to Ignore Saved As {filename}.csv")
