from decimal import Decimal

from rich.console import Console
from rich.table import Table

from application import Application
from models.account import Account
from models.balance import Balance


def accounts_menu(app: Application) -> None:
    print("\nACCOUNTS MENU")
    accounts = app.state.accounts
    while True:
        print_accounts(accounts)
        print("[a] -> Add New Account")
        print("[b] -> Back")
        try:
            choice = input("Enter An Account Number To Edit?: ")
            if choice == "b":
                print("BACK")
                return
            elif choice == "a":
                print("Adding Account")
                add_account(accounts)
            else:
                account = accounts[int(choice) - 1]
                print(f"You Have Picked {account}")
                edit_account(account)
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def edit_account(account: Account) -> None:
    print("\nACCOUNT EDITING")
    while True:
        print(f"Editing Account -> {account}")
        balance = account.balance
        assert balance is not None
        attributes = {
            "Name": {"value": account.name, "function": change_account_name},
            "Site Number": {
                "value": account.site_number,
                "function": change_account_site,
            },
            "Active": {"value": account.active, "function": change_account_active},
            "Annual Fees": {"value": balance.annual, "function": change_account_annual},
            "Remaining Fees": {
                "value": balance.remaining,
                "function": change_account_remaining,
            },
            "Outstanding Fees": {
                "value": balance.outstanding,
                "function": change_account_outstanding,
            },
            "Credit": {"value": balance.credit, "function": change_account_credit},
        }
        editable = [(name, action) for name, action in attributes.items()]
        for i, (name, action) in enumerate(editable, start=1):
            print(f"[{i}] -> {name}: {action['value']}")
        print("[p] -> Add Payment")
        print("[b] -> Back")
        try:
            choice = input("What would you like to change?: ")
            if choice == "b":
                print("BACK")
                return
            elif choice == "p":
                while True:
                    try:
                        amount = Decimal(input("Enter Amount: $"))
                        balance.add_payment(amount)
                        break
                    except ValueError:
                        print("Amount Must Be Monetary Amount")
            else:
                name, action = editable[int(choice) - 1]
                break
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")
    return action["function"](account)


def change_account_name(account: Account):
    new_name = input("Enter New Name: ")
    account.change_name(new_name)
    edit_account(account)


def change_account_site(account: Account):
    while True:
        try:
            new_site = input("Enter New Site Number: ")
            int(new_site)
            break
        except ValueError:
            print("Please Enter A Number")
    if len(new_site) == 1:
        new_site = f"0{new_site}"
    account.change_site(new_site)
    edit_account(account)


def change_account_active(account: Account):
    account.switch_active()
    edit_account(account)


def change_account_annual(account: Account):
    assert account.balance is not None
    while True:
        try:
            new_annual = Decimal(input("Enter New Amount: $"))
            break
        except ValueError:
            print("Please Enter A Number")
    account.balance.annual = new_annual
    edit_account(account)


def change_account_remaining(account: Account):
    assert account.balance is not None
    while True:
        try:
            new_remaining = Decimal(input("Enter New Amount: $"))
            break
        except ValueError:
            print("Please Enter A Number")
    account.balance.remaining = new_remaining
    edit_account(account)


def change_account_outstanding(account: Account):
    assert account.balance is not None
    while True:
        try:
            new_outstanding = Decimal(input("Enter New Amount: $"))
            break
        except ValueError:
            print("Please Enter A Number")
    account.balance.outstanding = new_outstanding
    edit_account(account)


def change_account_credit(account: Account):
    assert account.balance is not None
    while True:
        try:
            new_credit = Decimal(input("Enter New Amount: $"))
            break
        except ValueError:
            print("Please Enter A Number")
    account.balance.outstanding = new_credit
    edit_account(account)


def add_account(accounts: list[Account]) -> None:
    while True:
        try:
            site = input("Site Number: ")
            int(site)
            break
        except ValueError:
            print("Please Enter A Number")
    name = input("Account Holder Name: ")
    new_account = Account(
        site_number=site,
        name=name,
        balance=Balance(
            account_id=None,
            site_number=site,
            annual="7550",
            remaining="0",
            outstanding="0",
            pay_frequency="m",
        ),
    )
    for account in accounts:
        if account.site_number == new_account.site_number and account.active:
            assert account.balance is not None
            assert new_account.balance is not None
            new_account.balance.annual = account.balance.annual
            account.switch_active()
    accounts.append(new_account)


def print_accounts(accounts: list[Account]) -> None:
    console = Console()
    table = Table()
    table.add_column("Index")
    table.add_column("Site")
    table.add_column("Name")
    table.add_column("Remaining")
    table.add_column("Outstanding")
    table.add_column("Credit")
    index = 1
    for account in accounts:
        assert account.balance is not None
        balance = account.balance
        on_track = not balance.check_on_track()
        style = "red" if on_track else "green"
        table.add_row(
            f"{index}",
            f"{account.site_number}",
            f"{account.name}",
            f"[{style}]${balance.remaining:,.2f}[/{style}]",
            f"[{style}]${balance.outstanding:,.2f}[/{style}]",
            f"[{style}]${balance.credit:,.2f}[/{style}]",
        )
        index += 1
    console.print(table)


def account_picker(accounts: list[Account]) -> Account | None:
    print_accounts(accounts)
    print("[n] -> No Account")
    while True:
        try:
            choice = input("Which Account?: ")
            if choice == "n":
                print("No Match For This Transaction")
                return
            account = accounts[int(choice) - 1]
            break
        except (IndexError, ValueError):
            print("Invalid Choice. Please Choose From List")
    print(f"You Have Picked {account}")
    return account
