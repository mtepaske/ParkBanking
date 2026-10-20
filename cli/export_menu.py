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


def export_menu(app: Application) -> None:
    print("EXPORT MENU")
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
    accounts = app.state.accounts
    balances = []
    for account in accounts:
        balances.append(account.balance)
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    export_accounts_to_csv(accounts, f"files/{last_month} {last_month_year} - Accounts")
    print(f"Accounts saved as {last_month} {last_month_year} - Accounts.csv")
    export_balances_to_csv(balances, f"files/{last_month} {last_month_year} - Balances")
    print(f"Balances saved as {last_month} {last_month_year} - Balances.csv")


def export_payments(app: Application):
    transactions = app.state.transactions
    source_file = "Transactions.csv"
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    try:
        shutil.copy2(source_file, f"files/{last_month} {last_month_year} Raw.csv")
        print(f"{source_file} Saved as {last_month} {last_month_year} Raw.csv")
    finally:
        export_payments_to_csv(
            transactions, f"files/{last_month} {last_month_year}.csv"
        )
        print(f"Matched payments saved as {last_month} {last_month_year}.csv")


def export_words_to_ignore(app: Application):
    ignore = app.state.words_to_ignore
    last_month_date = dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(
        months=1
    )
    last_month = last_month_date.strftime("%B")
    last_month_year = last_month_date.strftime("%Y")
    export_ignore_to_csv(
        ignore, f"files/{last_month} {last_month_year} - WordsToIgnore.csv"
    )
    print(
        f"Words to Ignore Saved As {last_month} {last_month_year} - WordsToIgnore.csv"
    )
