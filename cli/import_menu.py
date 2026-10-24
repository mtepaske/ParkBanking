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
    old_accounts = app.state.accounts
    append = get_setting("append_accounts_on_import")
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
        new_accounts = import_account_info_from_csv(
            accounts_filename, balances_filename
        )
    except FileNotFoundError:
        print(
            f"One or Both Files Named {accounts_filename}.csv & {balances_filename}.csv Not Found"
        )
        return
    print("Accounts Information Imported")
    if append == "Always":
        app.append_accounts(new_accounts)
        print("Accounts Added")
        return
    elif append == "Never":
        app.state.accounts = new_accounts
        print("Accounts Replaced")
        return
    else:
        if len(old_accounts) > 0:
            print(f"{len(old_accounts)} Previously Loaded Accounts Found\n")
            while True:
                print("[a] -> Add")
                print("[r] -> Replace")
                print("[c] -> Cancel")
                confirmation = input(
                    "Would You Like To Add To Or Replace Previously Loaded Accounts?: "
                )
                if confirmation == "a":
                    try:
                        app.append_accounts(new_accounts)
                    except ValueError:
                        print("Aborting Replacement")
                    print("Accounts Added")
                    return
                elif confirmation == "r":
                    app.state.accounts = new_accounts
                    print("Accounts Replaced")
                    return
                elif confirmation == "c":
                    print("Cancelling Import")
                    return
                else:
                    print("Invalid Choice. Please Choose From List")


def import_banking(app: Application) -> None:
    print("\nIMPORTING BANKING DATA")
    old_transactions = app.state.transactions
    append = get_setting("append_transactions_on_import")
    print("[b] -> Back")
    print("[d] -> Default File Name (Transactions)")
    filename = input("Enter File Name: ")
    if filename == "b":
        print("BACK")
        return
    elif filename == "d":
        filename = "Transactions"
    try:
        new_transactions = import_payments(filename)
    except FileNotFoundError:
        print(f"No File Named {filename}.csv Found")
        return
    print("Banking Data Imported")
    if append == "Always":
        try:
            app.append_transactions(new_transactions)
        except ValueError:
            print("Aborting Replacement")
        print("Transactions Added")
        return
    elif append == "Never":
        app.state.transactions = new_transactions
        print("Transactions Replaced")
        return
    else:
        if len(old_transactions) > 0:
            print(f"{len(old_transactions)} Previously Loaded Transactions Found\n")
            while True:
                print("[a] -> Add")
                print("[r] -> Replace")
                print("[c] -> Cancel")
                confirmation = input(
                    "Would You Like To Add To Or Replace Previously Loaded Transactions?: "
                )
                if confirmation == "a":
                    try:
                        app.append_transactions(new_transactions)
                    except ValueError:
                        print("Aborting Replacement")
                    print("Transactions Added")
                    return
                elif confirmation == "r":
                    app.state.transactions = new_transactions
                    print("Transactions Replaced")
                    return
                elif confirmation == "c":
                    print("Cancelling Import")
                    return
                else:
                    print("Invalid Choice. Please Choose From List")


def import_mached_transactions(app: Application):
    print("\nIMPORTING MATCHED TRANSACTIONS")
    accounts = app.state.accounts
    old_transactions = app.state.transactions
    append = get_setting("append_transactions_on_import")
    filepath = input("Enter File Name: ")
    try:
        while True:
            new_transactions = import_matched(filepath, accounts)
            break
    except FileNotFoundError:
        print(f"No File Named {filepath}.csv Found")
        return
    review_matches(new_transactions, accounts)
    print("Matched Transactions Imported")
    if append == "Always":
        try:
            app.append_transactions(new_transactions)
        except ValueError:
            print("Aborting Replacement")
        print("Transactions Added")
        return
    elif append == "Never":
        app.state.transactions = new_transactions
        print("Transactions Replaced")
        return
    else:
        if len(old_transactions) > 0:
            print(f"{len(old_transactions)} Previously Loaded Transactions Found\n")
            while True:
                print("[a] -> Add")
                print("[r] -> Replace")
                print("[c] -> Cancel")
                confirmation = input(
                    "Would You Like To Add To Or Replace Previously Loaded Transactions?: "
                )
                if confirmation == "a":
                    try:
                        app.append_transactions(new_transactions)
                    except ValueError:
                        print("Aborting Replacement")
                    print("Transactions Added")
                    return
                elif confirmation == "r":
                    app.state.transactions = new_transactions
                    print("Transactions Replaced")
                    return
                elif confirmation == "c":
                    print("Cancelling Import")
                    return
                else:
                    print("Invalid Choice. Please Choose From List")
