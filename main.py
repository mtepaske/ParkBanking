import datetime as dt
import shutil
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from account import Account
from balance import Balance
from files import (
    export_balances,
    exportAccounts,
    exportPayments,
    exportWordsToIgnore,
    import_balances,
    importAccounts,
    importPayments,
    importWordsToIgnore,
)
from match import Matcher
from transactions import Transaction

"""
To add
- Seperation and pausable steps on main.py
- Add payment function on main.py
- Document balance.py
- Rename all functions in snake_case
"""


def start_program():
    pass


def user_choice():
    pass


def import_accounts_and_balances() -> list[Account]:
    accounts = importAccounts("Accounts.csv")
    balances = import_balances("Balances.csv")
    print("Imported Accounts and Balances")
    if len(balances) != len(accounts):
        raise ValueError("Accounts and Balances do not match")
    for index in range(len(accounts)):
        account = accounts[index]
        balance = balances[index]
        print(account)
        balance.info()
        if balance.site != account.site:
            raise ValueError("Account and Balance site numbers do not match")
        account.add_balance(balance)
    print("Accounts and Balances Matched\nProgram Ready")
    return accounts


def import_payments() -> list[Transaction]:
    transactions = importPayments("Transactions.csv")
    print("Imported Transactions")
    return transactions


def match_transactions(
    accounts: list[Account], transactions: list[Transaction]
) -> list[str]:
    ignore = importWordsToIgnore("WordsToIgnore.csv")
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keywordMatch(transaction)
        matcher.match(transaction, possibilities)
    return ignore


def process_payments(transactions: list[Transaction]):
    for transaction in transactions:
        if transaction.account is None:
            raise ValueError("Transaction not matched")
        elif transaction.account.balance is None:
            raise ValueError("Account has no balance")
        else:
            transaction.account.balance.add_payment(transaction.amount)


def procces_unknown_words(matcher: Matcher):
    matcher.unknownWords()


def save_files(
    transactions: list[Transaction],
    accounts: list[Account],
    ignore: list[str],
    balances: list[Balance],
):
    last_month = (
        dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(months=1)
    ).strftime("%B")
    this_year = dt.datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y")
    shutil.copy2("Transactions.csv", f"{last_month}{this_year}Raw.csv")
    exportAccounts(accounts, "Accounts")
    print("Accounts saved as Accounts.csv")
    exportPayments(transactions, f"{last_month} {this_year}.csv")
    print(f"Matched Transactions saved as {last_month} {this_year}.csv")
    exportWordsToIgnore(ignore, "WordsToIgnore")
    print("Words saved as WordsToIgnore.csv")
    export_balances(balances, "Balances")
    print("Updated Balances saved as Balances.csv")
    print("Files Saved")


def exit_program(
    transactions: list[Transaction],
    accounts: list[Account],
    ignore: list[str],
    balances: list[Balance],
):
    print("Exiting Program")


if __name__ == "__main__":

    accounts = importAccounts("Accounts.csv")
    balances = import_balances("Balances.csv")
    print("Imported Accounts and Balances")
    if len(balances) != len(accounts):
        raise ValueError("Accounts and Balances do not match")
    for index in range(len(accounts)):
        account = accounts[index]
        balance = balances[index]
        print(account)
        balance.info()
        if balance.site != account.site:
            raise ValueError("Account and Balance site numbers do not match")
        account.add_balance(balance)
    print("Accounts and Balances Matched\nProgram Ready")

    transactions = importPayments("test.csv")
    print("Imported Transactions")

    ignore = importWordsToIgnore("WordsToIgnore.csv")
    print("Imported Words To Ignore")
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keywordMatch(transaction)
        matcher.match(transaction, possibilities)
    print("Transactions Matched")

    for transaction in transactions:
        if transaction.account is None:
            raise ValueError("Transaction not matched")
        elif transaction.account.balance is None:
            raise ValueError("Account has no balance")
        else:
            transaction.account.balance.add_payment(transaction.amount)
    print("Payments Proccesed")

    matcher.unknownWords()
    print("Unknown Words Matched")

    last_month = (
        dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(months=1)
    ).strftime("%B")
    this_year = dt.datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y")
    shutil.copy2("Transactions.csv", f"{last_month}{this_year}Raw.csv")
    exportAccounts(accounts, "Accounts")
    print("Accounts saved as Accounts.csv")
    exportPayments(transactions, f"{last_month} {this_year}.csv")
    print(f"Matched Transactions saved as {last_month} {this_year}.csv")
    exportWordsToIgnore(ignore, "WordsToIgnore")
    print("Words saved as WordsToIgnore.csv")
    export_balances(balances, "Balances")
    print("Updated Balances saved as Balances.csv")
    print("Files Saved")

    print("Exiting Program")
