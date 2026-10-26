import csv
import datetime as dt
from decimal import Decimal

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction
from services.date import end_of_fy, start_of_fy
from services.settings import APP_DIRECTORY, get_setting

# Sets the folder to import from based on current settings
import_folder = APP_DIRECTORY / get_setting("imports_folder")
import_folder.mkdir(parents=True, exist_ok=True)


def import_accounts(filename: str) -> list[Account]:
    """
    Imports a CSV file containing account information

    Args:
        filename: The name of the file to import

    Returns:
        A list of accounts imported from the CSV
    """

    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)
        return [Account.from_csv(row) for row in reader]


def import_balances(filename: str) -> list[Balance]:
    """
    Imports a CSV file containing balance information

    Args:
        filename: The name of the file to import

    Returns:
        A list of balance imported from the CSV
    """

    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)
        return [Balance.from_csv(row) for row in reader]


def import_words_to_ignore(filename: str) -> set[str]:
    """
    Imports a CSV file containing words to ignore

    Args:
        filename: The name of the file to import

    Returns:
        A list of words imported from the CSV
    """

    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)
        return {row["Words"] for row in reader}


def import_payments(filename: str) -> list[Transaction]:
    """
    Imports a CSV file containing a bank statement

    Args:
        filename: The name of the file to import

    Returns:
        A list of transactions imported from the CSV
    """

    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:

        transactions = []
        reader = csv.DictReader(file)
        for row in reader:

            # Skip withdrawals and CASH deposits
            if Decimal(row["Amount"]) < 0:
                continue
            if row["Transaction Details"] == "CASH":
                continue
            transactions.append(Transaction.from_csv(row))

        return transactions


def import_matched(filename: str, accounts: list[Account]) -> list[Transaction]:
    """
    Imports a CSV file containing previously matched transaction information

    Args:
        filename: The name of the file to import
        accounts: The list of accounts a payment could be matched too

    Returns:
        A list of transactions imported from the CSV
    """

    with open(
        f"{import_folder / filename}.csv", newline="", encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)
        return [Transaction.from_matched_csv(row, accounts) for row in reader]


def import_account_info_from_csv(
    accounts_file: str, balances_file: str
) -> tuple[list[Account], list[Transaction]]:
    """
    Imports accounts and their assocciated balances from CSV files

    Args:
        accounts_file: The name of the file containing account information
        balances_file: The name of the file containing balance information

    Returns:
        The account information, as well as a generated history of payments

    Raises:
        ValueError: If an imported balance account ID does not match the imported accounts ID
    """

    accounts = import_accounts(accounts_file)
    balances = import_balances(balances_file)
    old_charges = []

    # Match accounts to balances based on site number
    for account in accounts:
        for balance in balances:
            if account.site_number == balance.site_number:

                # Checks for existing database ID's
                if (
                    account.account_id is not None
                    and balance.account_id is not None
                    and account.account_id != balance.account_id
                ):

                    raise ValueError("Balance ID does not match Account ID")

                account.add_balance(balance)
                break

        # If the account has never been inserted into a database, generate historical charges
        if account.account_id is None:
            old_charges.extend(add_annual_fees_to_history(account))

    return (accounts, old_charges)


def add_annual_fees_to_history(account: Account) -> list[Transaction]:
    """
    Generates historical payments from the outstanding fees and annual fees

    Args:
        account: The account to generate payments for

    Returns:
        A list of historical payments
    """

    assert account.balance is not None

    # Generate information for annual fee charge
    charges = []
    date = start_of_fy().strftime("%Y-%m-%d")
    amount = 0 - account.balance.annual
    details = f"Annual Fees {start_of_fy().year}/{end_of_fy().year}"

    # Apply annual fee charge
    annual_fee = Transaction(date, amount, details)
    annual_fee.account = account
    annual_fee.type = annual_fee.original_details
    charges.append(annual_fee)

    # Generate information for balance brought forward from untracked history
    date = (start_of_fy() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    amount = 0 - account.balance.outstanding
    details = "Brought Forward"

    # Apply brought forward charge
    brought_forward = Transaction(date, amount, details)
    brought_forward.account = account
    brought_forward.type = brought_forward.original_details
    charges.append(brought_forward)

    return charges
