from cli.menu import get_input
from models.account import Account
from models.balance import Balance
from services.database import AccountRepository, BalanceRepository, IgnoreRepository
from services.imports import import_words_to_ignore
from services.match import Matcher


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


def show_accounts(accounts: list[Account], balances: list[Balance]) -> None:
    """Shows all loaded accounts

    Args:
        accounts: (list[Account]) A list of accounts to show

    Returns:
        None
    """
    print("ACCOUNTS")
    Matcher.print_accounts(accounts)
    print("[a] - Add New Account")
    print("[b] -> Back")
    while True:
        try:
            choice = get_input("Which Account?")
            if choice == "b":
                print("Back")
                return
            elif choice == "a":
                print("Adding Account")
                add_account(accounts, balances)
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


def edit_account(account: Account) -> None:
    """Shows a list of options for editing a certain account

    Args:
        account: (Account) The account to edit

    Returns:
        None
    """
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


def add_account(accounts: list[Account], balances: list[Balance]) -> None:
    """Adds a new user account based on user input

    Args:
        accounts: (list[Account]) The list of current accounts
        balances: (list[Balance]) The list of current balances

    Returns:
        None
    """
    while True:
        try:
            site = get_input("Site Number")
            int(site)
            break
        except ValueError:
            print("Please enter a number")
    name = get_input("Account Holder Name")
    new_account = Account(site, name)
    for account in accounts:
        assert account.balance is not None
        if account.site == new_account.site and account.active:
            new_balance = Balance(
                account.id, new_account.site, str(account.balance.annual), "0", "0", "m"
            )
            account.switch_active()
            new_account.add_balance(new_balance)
            balances.append(new_balance)
    accounts.append(new_account)
