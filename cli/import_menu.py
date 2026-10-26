from application import Application
from cli.matching import review_matches
from services.imports import (
    import_account_info_from_csv,
    import_matched,
    import_payments,
)
from services.settings import APP_DIRECTORY, get_setting

# Sets the folder to import from based on current settings
import_folder = APP_DIRECTORY / get_setting("imports_folder")


def import_menu(app: Application) -> None:
    """
    Displays the imports menu

    Args:
        app: The instance of the application
    """

    # The available actions in the import menu
    import_actions = {
        "Import Accounts": import_accounts_from_csv,
        "Import Bank Statement": import_banking,
        "Import Matched Transactions": import_mached_transactions,
    }

    while True:

        print("\nIMPORT MENU")
        print(f"\nDefault Import Folder: {import_folder}")

        # Displays available actions and prompts user
        available = [(name, _) for name, _ in import_actions.items()]
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
            import_actions[name](app=app)
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def import_accounts_from_csv(app: Application) -> None:
    """
    Imports accounts information from a CSV file

    Args:
        app: The instance of the application
    """

    print("\nIMPORTING ACCOUNTS INFORMATION")
    old_accounts = app.state.accounts

    # Find the append accounts setting
    append = get_setting("append_accounts_on_import")

    # Prompts user for filename to import
    print("[b] -> Back")
    print("[d] -> Default File Name (Accounts)")
    accounts_filename = input("Enter File Name For Accounts: ")

    # Back action
    if accounts_filename == "b":
        print("BACK")
        return

    # Default filename
    elif accounts_filename == "d":
        accounts_filename = "Accounts"

    # Prompts user for filename to import
    print("[b] -> Back")
    print("[d] -> Default File Name (Balances)")
    balances_filename = input("Enter File Name For Balances: ")

    # Back action
    if balances_filename == "b":
        print("BACK")
        return

    # Default filename
    elif balances_filename == "d":
        balances_filename = "Balances"

    # Import files
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

    # If there is currently loaded accounts, action is taken based on append accounts settings
    if len(old_accounts) > 0:

        # Append the imported accounts to current loaded accounts
        if append == "Always":
            try:
                app.append_accounts(new_accounts[0])
            except ValueError:
                print("Aborting Import")
                return
            app.state.payments.extend(new_accounts[1])
            print("Accounts Added")
            return

        # Replace the current loaded accounts with imported accounts
        elif append == "Never":
            app.state.accounts = new_accounts[0]
            app.state.payments.extend(new_accounts[1])
            print("Accounts Replaced")
            return

        # Prompt the user for choice
        else:
            print(f"{len(old_accounts)} Previously Loaded Accounts Found\n")
            while True:
                print("[a] -> Add")
                print("[r] -> Replace")
                print("[c] -> Cancel")
                confirmation = input(
                    "Would You Like To Add To Or Replace Previously Loaded Accounts?: "
                )

                # Append the imported accounts to current loaded accounts
                if confirmation == "a":
                    try:
                        app.append_accounts(new_accounts[0])
                        app.state.payments.extend(new_accounts[1])
                    except ValueError:
                        print("Aborting Replacement")
                        return
                    print("Accounts Added")
                    return

                # Replace the current loaded accounts with imported accounts
                elif confirmation == "r":
                    app.state.accounts = new_accounts[0]
                    app.state.payments.extend(new_accounts[1])
                    print("Accounts Replaced")
                    return

                # Cancel import
                elif confirmation == "c":
                    print("Cancelling Import")
                    return

                else:
                    print("Invalid Choice. Please Choose From List")

    else:
        app.state.accounts = new_accounts[0]
        app.state.payments.extend(new_accounts[1])
        print("Accounts Added")


def import_banking(app: Application) -> None:
    """
    Imports banking information from a CSV file

    Args:
        app: The instance of the application
    """

    print("\nIMPORTING BANKING DATA")
    old_transactions = app.state.transactions

    # Find the append transactions setting
    append = get_setting("append_transactions_on_import")

    # Prompts user for filename to import
    print("[b] -> Back")
    print("[d] -> Default File Name (Transactions)")
    filename = input("Enter File Name: ")

    # Back action
    if filename == "b":
        print("BACK")
        return

    # Default filename
    elif filename == "d":
        filename = "Transactions"

    # Import file
    try:
        new_transactions = import_payments(filename)
    except FileNotFoundError:
        print(f"No File Named {filename}.csv Found")
        return
    print("Banking Data Imported")

    # If there is currently loaded transactions, action is taken based on append transactions settings
    if len(old_transactions) > 0:

        # Append the imported transactions to current loaded transactions
        if append == "Always":
            try:
                app.append_transactions(new_transactions)
            except ValueError:
                print("Aborting Import")
                return
            print("Transactions Added")
            return

        # Replace the current loaded transactions with imported transactions
        elif append == "Never":
            app.state.transactions = new_transactions
            print("Transactions Replaced")
            return

        # Prompt the user for choice
        else:
            print(f"{len(old_transactions)} Previously Loaded Transactions Found\n")
            while True:
                print("[a] -> Add")
                print("[r] -> Replace")
                print("[c] -> Cancel")
                confirmation = input(
                    "Would You Like To Add To Or Replace Previously Loaded Transactions?: "
                )

                # Append the imported transactions to current loaded transactions
                if confirmation == "a":
                    try:
                        app.append_transactions(new_transactions)
                    except ValueError:
                        print("Aborting Replacement")
                    print("Transactions Added")
                    return

                # Replace the current loaded transactions with imported transactions
                elif confirmation == "r":
                    app.state.transactions = new_transactions
                    print("Transactions Replaced")
                    return

                # Cancel Import
                elif confirmation == "c":
                    print("Cancelling Import")
                    return

                else:
                    print("Invalid Choice. Please Choose From List")

    else:
        app.state.transactions = new_transactions
        print("Transactions Added")


def import_mached_transactions(app: Application):
    """
    Imports previously matched transactions from a CSV file

    Args:
        app: The instance of the application
    """

    print("\nIMPORTING MATCHED TRANSACTIONS")
    accounts = app.state.accounts
    old_transactions = app.state.transactions

    # Find the append transactions setting
    append = get_setting("append_transactions_on_import")

    # Prompts user for filename to import
    print("[b] -> Back")
    filename = input("Enter File Name: ")

    # Back action
    if filename == "b":
        print("BACK")
        return

    # Import file
    try:
        new_transactions = import_matched(filename, accounts)
    except FileNotFoundError:
        print(f"No File Named {filename}.csv Found")
        return
    print("Matched Transactions Imported")

    # Review matches
    review_matches(new_transactions, accounts)

    # If there is currently loaded transactions, action is taken based on append transactions settings
    if len(old_transactions) > 0:

        # Append the imported transactions to current loaded transactions
        if append == "Always":
            try:
                app.append_transactions(new_transactions)
            except ValueError:
                print("Aborting Import")
                return
            print("Transactions Added")
            return

        # Replace the current loaded transactions with imported transactions
        elif append == "Never":
            app.state.transactions = new_transactions
            print("Transactions Replaced")
            return

        # Prompt the user for choice
        else:
            print(f"{len(old_transactions)} Previously Loaded Transactions Found\n")
            while True:
                print("[a] -> Add")
                print("[r] -> Replace")
                print("[c] -> Cancel")
                confirmation = input(
                    "Would You Like To Add To Or Replace Previously Loaded Transactions?: "
                )

                # Append the imported transactions to current loaded transactions
                if confirmation == "a":
                    try:
                        app.append_transactions(new_transactions)
                    except ValueError:
                        print("Aborting Replacement")
                    print("Transactions Added")
                    return

                # Replace the current loaded transactions with imported transactions
                elif confirmation == "r":
                    app.state.transactions = new_transactions
                    print("Transactions Replaced")
                    return

                # Cancel Import
                elif confirmation == "c":
                    print("Cancelling Import")
                    return

                else:
                    print("Invalid Choice. Please Choose From List")

    else:
        app.state.transactions = new_transactions
        print("Transactions Added")
