from models.account import Account
from models.balance import Balance


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
    new_account = Account(site, name)
    for account in accounts:
        assert account.balance is not None
        if account.site_number == new_account.site_number and account.active:
            new_balance = Balance(
                account.account_id,
                new_account.site_number,
                str(account.balance.annual),
                "0",
                "0",
                "m",
            )
            account.switch_active()
            new_account.add_balance(new_balance)
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
