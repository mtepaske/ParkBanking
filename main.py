import datetime as dt
import shutil
from typing import TypedDict
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from account import Account
from balance import Balance
from files import (
    export_accounts,
    export_balances,
    export_payments,
    export_words_to_ignore,
    import_accounts,
    import_balances,
    import_payments,
    import_words_to_ignore,
)
from match import Matcher
from transactions import Transaction


class AppState(TypedDict):
    accounts: list[Account] | None
    balances: list[Balance] | None
    transactions: list[Transaction] | None
    words_to_ignore: list[str] | None
    matcher: Matcher | None
    payments: list[Transaction] | None


state: AppState = {
    "accounts": None,
    "balances": None,
    "transactions": None,
    "words_to_ignore": None,
    "matcher": None,
    "payments": None,
}


def start_program() -> bool:
    while True:
        test = input("Is this a test run? (y/n):")
        if test == "y":
            test = True
            print("Test Initialised")
            break
        elif test == "n":
            test = False
            print("Starting Program")
            break
        else:
            print("Choice must be y or n")
    return test


def show_menu():
    while True:
        available_actions = [
            (name, action) for name, action in actions.items() if action["available"]
        ]
        for i, (name, action) in enumerate(available_actions, start=1):
            print(f"{i} -> {name}")
        choice = int(input("Choose an action: "))
        try:
            name, action = available_actions[choice - 1]
            return action["function"]()
        except IndexError:
            print("Invalid choice. Please choose from list")


def import_accounts_and_balances() -> tuple[list[Account], list[Balance]]:
    accounts = import_accounts("Accounts.csv")
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
    return (accounts, balances)


def import_accounts_and_balances_action():
    acts_and_bal = import_accounts_and_balances()
    state["accounts"] = acts_and_bal[0]
    state["balances"] = acts_and_bal[1]


def import_banking() -> list[Transaction]:
    transactions = import_payments("Transactions.csv")
    print("Imported Transactions")
    return transactions


def import_banking_action():
    state["transactions"] = import_banking()


def match_transactions(
    accounts: list[Account], transactions: list[Transaction]
) -> tuple[list[str], Matcher]:
    ignore = import_words_to_ignore("WordsToIgnore.csv")
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keyword_match(transaction)
        matcher.match(transaction, possibilities)
    return (ignore, matcher)


def match_transactions_action():
    if state["accounts"] is not None and state["transactions"] is not None:
        matched_info = match_transactions(state["accounts"], state["transactions"])
        state["words_to_ignore"] = matched_info[0]
        state["matcher"] = matched_info[1]
    else:
        print("Accounts and Transactions not imported")


def process_payments(transactions: list[Transaction]):
    for transaction in transactions:
        if transaction.account is None:
            raise ValueError("Transaction not matched")
        elif transaction.account.balance is None:
            raise ValueError("Account has no balance")
        else:
            transaction.account.balance.add_payment(transaction.amount)


def process_payments_action():
    if state["transactions"] is not None:
        process_payments(state["transactions"])


def procces_unknown_words(matcher: Matcher):
    matcher.unknown_words()


def procces_unknown_words_action():
    if state["matcher"] is not None and state["words_to_ignore"] is not None:
        state["matcher"].unknown_words()


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
    export_accounts(accounts, "Accounts")
    print("Accounts saved as Accounts.csv")
    export_payments(transactions, f"{last_month} {this_year}.csv")
    print(f"Matched Transactions saved as {last_month} {this_year}.csv")
    export_words_to_ignore(ignore, "WordsToIgnore")
    print("Words saved as WordsToIgnore.csv")
    export_balances(balances, "Balances")
    print("Updated Balances saved as Balances.csv")
    print("Files Saved")


def save_files_action():
    transactions = state["transactions"]
    accounts = state["accounts"]
    ignore = state["words_to_ignore"]
    balance = state["balances"]
    if (
        transactions is not None
        and accounts is not None
        and ignore is not None
        and balance is not None
    ):
        save_files(transactions, accounts, ignore, balance)
    else:
        print("All files not loaded")


def exit_program():
    print("Exiting Program")


if __name__ == "__main__":

    actions = {
        "Import Accounts & Balances": {
            "available": True,
            "function": import_accounts_and_balances_action,
        },
        "Import Banking Data": {"available": True, "function": import_banking_action},
        "Match Transactions to Accounts": {
            "available": False,
            "function": match_transactions,
        },
        "Proccess Payments": {"available": False, "function": process_payments_action},
        "Proccess Unknown Words": {
            "available": False,
            "function": procces_unknown_words_action,
        },
        "Save Files": {"available": False, "function": save_files_action},
        "Exit Program": {"available": True, "function": exit_program},
    }
