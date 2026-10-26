from decimal import Decimal

from rich.columns import Columns
from rich.console import Console
from rich.table import Table

from application import Application
from models.account import Account
from models.balance import Balance, money
from models.transactions import Transaction
from services.date import (
    end_of_fy,
    get_date_from_str_iso,
    get_str_from_date,
    start_of_fy,
)
from services.settings import get_setting


def accounts_menu(app: Application) -> None:
    """
    Displays the account menu and gets user input

    Args:
        app: The instance of the application
    """

    while True:

        print("\nACCOUNTS MENU")
        accounts = app.state.accounts

        # Displays accounts and available options and prompts user
        print_accounts(accounts)
        print("[a] -> Add New Account")
        print("[b] -> Back")
        choice = input("Enter An Account Number To View?: ")

        # Back action
        if choice == "b":
            print("BACK")
            return

        # Add new account action
        elif choice == "a":
            print("Adding Account")
            add_account(accounts)

        else:
            # Opens the edit account and payment history menu for a chosen account
            try:
                account = accounts[int(choice) - 1]
                print(f"You Have Picked {account}")
                # Displays the edit account acctions
                added_payments = edit_account(account, app=app)

                # Adds any added payments to the loaded payments
                app.state.payments.extend(added_payments)

            except (ValueError, IndexError):
                print("Invalid Choice. Please Choose From List")


def payment_history(account: Account, payments: list[Transaction]) -> None:
    """
    Displays the payment history of an account

    Args:
        account: The account to display the history of
        payments: The payments to display
    """

    assert account.balance is not None

    print("\nPAYMENT HISTORY")
    print(f"History For {account}")

    # Finds the latest balance
    running_balance = account.balance.balance
    rows = []

    # Makes the display table
    console = Console()
    table = Table(show_lines=True)
    table.add_column("Date")
    table.add_column("Particulars")
    table.add_column("Debit")
    table.add_column("Credit")
    table.add_column("Balance")

    # Sort payments by date so newest payment is first
    payments.sort(key=lambda t: t.date, reverse=True)

    for payment in payments:

        # Is payment is positive display as credit
        if payment.amount > 0:
            rows.append(
                (
                    f"{payment.date}",
                    f"{payment.type}",
                    "",
                    f"${payment.amount:,.2f}",
                    f"${running_balance:,.2f}",
                )
            )
            running_balance += payment.amount

        # If payment is positive display as debit
        else:
            amount = abs(payment.amount)
            rows.append(
                (
                    f"{payment.date}",
                    f"{payment.type}",
                    f"${amount:,.2f}",
                    "",
                    f"${running_balance:,.2f}",
                )
            )
            running_balance -= amount

    # Revers the rows so oldest payment first
    rows.reverse()

    # Add rows to display table and display table
    for date, particulars, debit, credit, balance in rows:
        table.add_row(
            date,
            particulars,
            f"[red]{debit}[/red]",
            f"[green]{credit}[/green]",
            balance,
        )
    console.print(table)


def edit_account(account: Account, app: Application) -> list[Transaction]:
    """
    Displays current account information and prompts user for input to edit it

    Args:
        account: The account to display the information of

    Returns:
        A list of any added payments
    """

    balance = account.balance
    assert balance is not None
    payments = []

    while True:

        # The current attributes and the functions for changing them
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

        # Gets the payment history from the database if it exists
        if account.account_id is not None:
            history = app.repos.account_repo.get_payments(account.account_id)
        else:
            history = []

        # Gets the payments not loaded into the database
        for payment in app.state.payments:
            if payment.account == account:
                history.append(payment)

        # Gets any recently added payments
        for payment in payments:
            history.append(payment)

        # Displays the payment history
        payment_history(account, history)

        print("\nACCOUNT EDITING")
        print(f"Editing Account -> {account}")

        # Displays the available actions and prompts user
        editable = [(name, action) for name, action in attributes.items()]
        for i, (name, action) in enumerate(editable, start=1):
            print(f"[{i}] -> {name}: {action['value']}")
        print("[p] -> Add Payment")
        print("[c] -> Add Charge")
        print("[b] -> Back")
        choice = input("What would you like to change?: ")

        # Back action
        if choice == "b":
            print("BACK")
            return payments

        # Add payment action
        elif choice == "p":
            payment = add_manual_payment(account)
            if payment is None:
                continue
            else:
                payments.append(payment)

        # Add charge action
        elif choice == "c":
            charge = add_manual_charge(account)
            if charge is None:
                continue
            else:
                payments.append(charge)

        # Calls action chosen by user
        else:
            try:
                name, action = editable[int(choice) - 1]
                action["function"](account)
            except (ValueError, IndexError):
                print("Invalid Choice. Please Choose From List")


def add_manual_payment(account: Account) -> Transaction | None:
    """
    Prompts user to enter information for a manual payment

    Args:
        account: The account to add the payment too

    Returns:
        The payment defined using information from the user
    """

    balance = account.balance
    assert balance is not None

    while True:

        # Prompts user for payment date
        print("[b] -> Back")
        date = input("Enter Date (yyyy-mm-dd): ")

        # Back action
        if date == "b":
            print("BACK")
            return

        # Data validation
        try:
            get_date_from_str_iso(date)
            break
        except ValueError:
            print("Incorrect Date Format. Please Use yyyy-mm-dd")

    while True:

        # Prompt user for payment amount
        print("[b] -> Back")
        amount = input("Enter Amount: $")

        # Back action
        if amount == "b":
            print("BACK")
            return

        # Data validation
        try:
            amount = money(amount)
            break
        except ValueError:
            print("Must Be Monetary Amount")

    while True:

        # Displays options and gets user input for description of payment
        print("[b] -> Back")
        print("[m] -> Cash")
        print("[d] -> Direct Debit")
        print("[c] -> Credit Card")
        print("[u] -> Custom Description")
        choice = input("Please Choose A Description For The Payment: ")

        # Back action
        if amount == "b":
            print("BACK")
            return

        # Sets description as user choice
        elif choice == "m":
            description = "CASH"
            break
        elif choice == "d":
            description = "Direct Debit"
            break
        elif choice == "c":
            description = "Credit Card"
            break
        elif choice == "u":
            description = input("Enter Custom Description: ")
            break
        else:
            print("Invalid Choice. Please Choose From List")

    # Adds the payment to the balance and payment history
    balance.add_payment(amount)
    payment = Transaction(date, amount, description, description)
    payment.account = account

    return payment


def add_manual_charge(account: Account) -> Transaction | None:
    """
    Prompts user to enter information for a manual charge

    Args:
        account: The account to add the charge= too

    Returns:
        The charge defined using information from the user
    """

    balance = account.balance
    assert balance is not None

    while True:

        # Prompts user for charge date
        print("[b] -> Back")
        date = input("Enter Date (yyyy-mm-dd): ")

        # Back action
        if date == "b":
            print("BACK")
            return

        # Data validation
        try:
            date = get_date_from_str_iso(date)
            break
        except ValueError:
            print("Incorrect Date Format. Please Use yyyy-mm-dd")

    while True:

        # Prompt user for charge amount
        print("[b] -> Back")
        amount = input("Enter Amount: $")

        # Back action
        if amount == "b":
            print("BACK")
            return

        # Data validation
        try:
            amount = money(amount)
            break
        except ValueError:
            print("Must Be Monetary Amount")

    while True:

        # Displays options and gets user input for description of payment
        print("[b] -> Back")
        print("[a] -> Annual Fees")
        print("[u] -> Custom Description")
        choice = input("Please Choose A Description For The Payment: ")

        # Back action
        if amount == "b":
            print("BACK")
            return

        # Sets description as annual fees
        elif choice == "a":

            # Sets date of annual fees by annual period setting
            if get_setting("annual_period") == "FY":
                start_year = start_of_fy(date).year
                end_year = end_of_fy(date).year
                period = f"{start_year}/{end_year}"
            elif get_setting("annual_period") == "CY":
                period = date.year
            else:
                raise ValueError("Setting for annual period invalid")

            # Sets description
            description = f"Annual Fees {period}"
            break

        # Gets user input for custom description
        elif choice == "u":
            description = input("Enter Custom Description: ")
            break

        else:
            print("Invalid Choice. Please Choose From List")

    # Adds the charge to the balance and payment history
    balance.add_payment(amount)
    charge = Transaction(get_str_from_date(date), 0 - amount, description, description)
    charge.account = account

    return charge


def change_account_name(account: Account):
    """
    Changes the name of the primary site holder

    Args:
        account: The account to edit
    """

    new_name = input("Enter New Name: ")
    account.change_name(new_name)


def change_account_site(account: Account):
    """
    Change the site number for an account

    Args:
        account: The account to edit
    """

    while True:

        # Gets and validates user input
        new_site = input("Enter New Site Number: ")
        try:
            int(new_site)
            break
        except ValueError:
            print("Please Enter A Number")

    # Normalises site number to 2 digits
    if len(new_site) == 1:
        new_site = f"0{new_site}"

    account.change_site(new_site)


def change_account_active(account: Account):
    """
    Changes the active status of the account

    Args:
        account: The account to edit
    """

    account.switch_active()


def change_account_annual(account: Account):
    """
    Changes the annual fees for an account

    Args:
        account: The account to edit
    """

    assert account.balance is not None

    while True:

        # Gets and validates user input
        try:
            new_annual = Decimal(input("Enter New Amount: $"))
            account.balance.annual = new_annual
            break
        except ValueError:
            print("Please Enter A Non Negative Number")


def change_account_remaining(account: Account):
    """
    Changes the remaining fees for an account

    Args:
        account: The account to edit
    """

    assert account.balance is not None

    while True:

        # Gets and validates user input
        try:
            new_remaining = Decimal(input("Enter New Amount: $"))
            account.balance.remaining = new_remaining
            break
        except ValueError:
            print("Please Enter A Non Negative Number")


def change_account_outstanding(account: Account):
    """
    Change the outstanding fees for an account

    Args:
        account: The account to edit
    """

    assert account.balance is not None

    while True:

        # Gets and validates user input
        try:
            new_outstanding = Decimal(input("Enter New Amount: $"))
            account.balance.outstanding = new_outstanding
            break
        except ValueError:
            print("Please Enter A Non Negative Number")


def change_account_credit(account: Account):
    """
    Change the credit for an account

    Args:
        account: The account to edit
    """

    assert account.balance is not None

    while True:

        # Gets and validates user input
        try:
            new_credit = Decimal(input("Enter New Amount: $"))
            account.balance.outstanding = new_credit
            break
        except ValueError:
            print("Please Enter A Number")


def add_account(accounts: list[Account]) -> None:
    """
    Add a new account

    Args:
        accounts: The list of accounts to add too
    """

    while True:

        # Gets user input
        print("[b] -> Back")
        site = input("Site Number: ")

        # Back action
        if site == "b":
            print("BACK")
            return

        # Validates user input
        try:
            int(site)
            break
        except ValueError:
            print("Please Enter A Number")

    while True:

        # Gets user input
        print("[b] -> Back")
        name = input("Account Holder Name: ")

        # Back action
        if name == "b":
            print("BACK")
            return

        break

    # Initialises the new account
    new_account = Account(
        site_number=site,
        name=name,
        balance=Balance(
            account_id=None,
            site_number=site,
            annual="7550",
            remaining="7550",
            outstanding="0",
            pay_frequency="m",
        ),
    )

    # Checks for conflicts with current accounts
    for account in accounts:
        if account.site_number == new_account.site_number and account.active:
            assert account.balance is not None
            assert new_account.balance is not None
            new_account.balance.annual = account.balance.annual
            account.switch_active()

    while True:

        # Prints new account and prompts user for confirmation
        print(f"Adding: {new_account}")
        confirm = input("Add New Accoount? (y/n): ")

        # Add account
        if confirm == "y":
            accounts.append(new_account)
            return

        # Back action
        elif confirm == "n":
            print("BACK")
            return

        else:
            print("Please Choose y or n")


def print_accounts(accounts: list[Account]) -> None:
    """
    Displays a list of accounts

    Args:
        accounts: The accounts to display
    """

    # Makes 2 display tables
    console = Console()

    table1 = Table(show_lines=True)
    table1.add_column("Index")
    table1.add_column("Site")
    table1.add_column("Name")
    table1.add_column("Remaining")
    table1.add_column("Outstanding")
    table1.add_column("Credit")

    table2 = Table(show_lines=True)
    table2.add_column("Index")
    table2.add_column("Site")
    table2.add_column("Name")
    table2.add_column("Remaining")
    table2.add_column("Outstanding")
    table2.add_column("Credit")

    # Finds the midpoint of indexes
    midpoint = (len(accounts) + 1) // 2

    # Adds half the accounts to left table
    for i in range(midpoint):

        account = accounts[i]
        balance = account.balance
        assert balance is not None
        on_track = balance.check_on_track()

        # Color for display
        style = "green" if on_track else "red"

        # Add account informtion to table
        table1.add_row(
            f"[blue]{i + 1}[/blue]",
            f"{account.site_number}",
            f"{account.name}",
            f"[{style}]${balance.remaining:,.2f}[/{style}]",
            f"[{style}]${balance.outstanding:,.2f}[/{style}]",
            f"[{style}]${balance.credit:,.2f}[/{style}]",
        )

    # Adds the remaining accounts to right table
    for i in range(len(accounts) - midpoint):
        account = accounts[midpoint + i]
        balance = account.balance
        assert balance is not None
        on_track = not balance.check_on_track()

        # Color for display
        style = "red" if on_track else "green"

        # Add account informtion to table
        table2.add_row(
            f"[blue]{i + 1 + midpoint}[/blue]",
            f"{account.site_number}",
            f"{account.name}",
            f"[{style}]${balance.remaining:,.2f}[/{style}]",
            f"[{style}]${balance.outstanding:,.2f}[/{style}]",
            f"[{style}]${balance.credit:,.2f}[/{style}]",
        )

    # Displays the tables
    console.print(Columns([table1, table2], equal=True, expand=False))


def account_picker(accounts: list[Account]) -> Account | None:
    """
    Displays and promts the user to pick an account

    Args:
        accounts: The accounts to choose from

    Returns:
        The chosen account. None if no account chosen
    """

    while True:

        # Display the accounts and gets user input
        print_accounts(accounts)
        print("[n] -> No Account")
        choice = input("Which Account?: ")

        # No account
        if choice == "n":
            print("No Account Picked")
            return

        # Validates user input
        try:
            account = accounts[int(choice) - 1]
            break
        except (IndexError, ValueError):
            print("Invalid Choice. Please Choose From List")

    print(f"You Have Picked {account}")
    return account
