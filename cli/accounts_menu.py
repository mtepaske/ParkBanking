from application import Application
from models.account import Account
from models.balance import Balance


def accounts_menu(app: Application) -> None:
    print("ACCOUNTS MENU")
    show_accounts(app.state.accounts)


def show_accounts(accounts: list[Account]) -> None:
    print_accounts(accounts)
    print("[a] -> Add New Account")
    print("[b] -> Back")
    while True:
        try:
            choice = input("Which Account?: ")
            if choice == "b":
                print("BACK")
                return
            elif choice == "a":
                print("Adding Account")
                add_account(accounts)
                return
            else:
                account = accounts[int(choice) - 1]
                break
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")
    print(f"You Have Picked {account}")
    edit_account(account)


def edit_account(account: Account) -> None:
    attributes = {
        "Site Number": {
            "value": account.site_number,
            "function": account.change_site,
        },
        "Name": {"value": account.name, "function": account.change_name},
        "Active": {"value": account.active, "function": account.switch_active},
    }
    print(f"Editing Account: {account.site_number}, {account.name}")
    while True:
        editable = [(name, action) for name, action in attributes.items()]
        for i, (name, action) in enumerate(editable, start=1):
            print(f"[{i}] - {name}: {action['value']}")
        print("[b] -> Back")
        try:
            choice = input("What would you like to change?")
            if choice == "b":
                print("BACK")
                return
            else:
                name, action = editable[int(choice) - 1]
                break
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")
    return action["function"]()


def add_account(accounts: list[Account]) -> None:
    while True:
        try:
            site = input("Site Number")
            int(site)
            break
        except ValueError:
            print("Please enter a number")
    name = input("Account Holder Name")
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
    index = 1
    for account in accounts:
        assert account.balance is not None
        print(f"[{index}] -> {account.name}, Site {account.site_number}")
        index += 1
        balance = account.balance
        print(
            f"    Annual Fees: {balance.annual}, Remaining: {balance.remaining}, Outstanding: {balance.outstanding}, On Track: {balance.check_on_track()}"
        )


def account_picker(accounts: list[Account]) -> Account | None:
    print_accounts(accounts)
    print("[n] -> No Account")
    while True:
        try:
            choice = input("Which Account?")
            if choice == "n":
                print("No Match For This Transaction")
                return
            account = accounts[int(choice) - 1]
            break
        except (IndexError, ValueError):
            print("Invalid Choice. Please Choose From List")
    print(f"You Have Picked {account}")
    return account
