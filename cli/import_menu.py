from application import APP_DIRECTORY, Application
from cli.matching import review_matches
from services.imports import (
    import_account_info_from_csv,
    import_matched,
    import_payments,
)
from services.settings import get_setting

import_folder = APP_DIRECTORY / get_setting("import_folder")


def import_menu(app: Application) -> None:
    print("\nIMPORT MENU")
    print(f"\nDefault Import Folder: {import_folder}")
    import_actions = {
        "Import Accounts": import_accounts_from_csv,
        "Import Bank Statement": import_banking,
        "Import Matched Transactions": import_mached_transactions,
    }
    available = [(name, _) for name, _ in import_actions.items()]
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
    return import_actions[name](app=app)


def import_accounts_from_csv(app: Application) -> None:
    print("\nIMPORTING ACCOUNTS INFORMATION")
    print("[b] -> Back")
    print("[d] -> Default File Name (Accounts)")
    accounts_filename = input("Enter File Name For Accounts: ")
    if accounts_filename == "b":
        print("BACK")
        return
    elif accounts_filename == "d":
        accounts_filename = "Accounts"
    print("[b] -> Back")
    print("[d] -> Default File Name (Balances)")
    balances_filename = input("Enter File Name For Balances: ")
    if balances_filename == "b":
        print("BACK")
        return
    elif balances_filename == "d":
        balances_filename = "Balances"
    try:
        app.state.accounts = import_account_info_from_csv(
            accounts_filename, balances_filename
        )
        print("Accounts Information Imported")
    except FileNotFoundError:
        print(
            f"One or Both Files Named {accounts_filename}.csv & {balances_filename}.csv Not Found"
        )
        return


def import_banking(app: Application) -> None:
    print("\nIMPORTING BANKING DATA")
    print("[b] -> Back")
    print("[d] -> Default File Name (Transactions)")
    filename = input("Enter File Name: ")
    if filename == "b":
        print("BACK")
        return
    elif filename == "d":
        filename = "Transactions"
    try:
        app.state.transactions = import_payments(filename)
    except FileNotFoundError:
        print(f"No File Named {filename}.csv Found")
    print("Banking Data Imported")


def import_mached_transactions(app: Application):
    print("\nIMPORTING MATCHED TRANSACTIONS")
    accounts = app.state.accounts
    filepath = input("Enter File Name: ")
    try:
        while True:
            transactions = import_matched(filepath, accounts)
            app.state.transactions = transactions
            break
    except FileNotFoundError:
        print(f"No File Named {filepath}.csv Found")
        return
    review_matches(transactions, accounts)
    print("Matched Transactions Imported")
