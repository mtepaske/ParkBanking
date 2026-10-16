import argparse
import datetime as dt
import shutil
import sys
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


def start_program() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage Caravan Park Transactions and Accounts"
    )
    parser.add_argument("--test", action="store_true", help="Run program in test mode")
    args = parser.parse_args()
    if args.test:
        print("Starting in Test mode")
    else:
        print("Starting program")
    return args


def show_menu(test: bool = False) -> None:
    while True:
        available_actions = [
            (name, action) for name, action in actions.items() if action["available"]
        ]
        for i, (name, action) in enumerate(available_actions, start=1):
            print(f"{i} -> {name}")
        choice = int(input("Choose an action: "))
        try:
            name, action = available_actions[choice - 1]
            return action["function"](test)
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
        if balance.site != account.site:
            raise ValueError("Account and Balance site numbers do not match")
        account.add_balance(balance)
    print("Accounts and Balances Matched")
    actions["Import Accounts & Balances"]["available"] = False
    if state["transactions"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True
    return (accounts, balances)


def import_accounts_and_balances_action(test: bool = False) -> None:
    acts_and_bal = import_accounts_and_balances()
    state["accounts"] = acts_and_bal[0]
    state["balances"] = acts_and_bal[1]


def import_banking(test: bool = False) -> list[Transaction]:
    if test:
        transactions = import_payments("test.csv")
    else:
        transactions = import_payments("Transactions.csv")
    print("Imported Transactions")
    actions["Import Banking Data"]["available"] = False
    if state["accounts"] is not None and state["balances"] is not None:
        actions["Match Transactions to Accounts"]["available"] = True
    return transactions


def import_banking_action(test: bool = False) -> None:
    state["transactions"] = import_banking(test)


def match_transactions(
    accounts: list[Account], transactions: list[Transaction]
) -> tuple[list[str], Matcher]:
    ignore = import_words_to_ignore("WordsToIgnore.csv")
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keyword_match(transaction)
        matcher.match(transaction, possibilities)
    review_matches()
    actions["Match Transactions to Accounts"]["available"] = False
    actions["Proccess Payments"]["available"] = True
    actions["Proccess Unknown Words"]["available"] = True
    return (ignore, matcher)


def match_transactions_action(test: bool = False) -> None:
    if state["accounts"] is not None and state["transactions"] is not None:
        matched_info = match_transactions(state["accounts"], state["transactions"])
        state["words_to_ignore"] = matched_info[0]
        state["matcher"] = matched_info[1]
    else:
        print("Accounts and Transactions not imported")


def review_matches() -> None:
    if state["transactions"] is None:
        print("Transactions are not imported")
        return
    for transaction in state["transactions"]:
        account = transaction.account
        if account is None:
            print("Transaction has not being matched")
            print(f"{transaction.date}, ${transaction.amount}, {transaction.details}")
            continue
        print(
            f"{account.site}: {account.name} -> {transaction.amount} - {transaction.details}"
        )
    while True:
        choice = input("Are all the transactions matched correctly?: (y/n)")
        if choice == "y":
            print("Transactions macthed successfully")
            return
        else:
            print("Transaction matching failed. Terminal failure. Exiting program")
            exit_program()


def process_payments(transactions: list[Transaction]) -> None:
    for transaction in transactions:
        if transaction.account is None:
            raise ValueError("Transaction not matched")
        elif transaction.account.balance is None:
            raise ValueError("Account has no balance")
        else:
            transaction.account.balance.add_payment(transaction.amount)
    actions["Proccess Payments"]["available"] = False


def process_payments_action(test: bool = False) -> None:
    if state["transactions"] is not None:
        process_payments(state["transactions"])


def procces_unknown_words(matcher: Matcher) -> None:
    matcher.unknown_words()
    state["words_to_ignore"] = matcher.ignore
    actions["Proccess Unknown Words"]["available"] = False


def procces_unknown_words_action(test: bool = False) -> None:
    if state["matcher"] is not None and state["words_to_ignore"] is not None:
        procces_unknown_words(state["matcher"])


def save_files(
    transactions: list[Transaction] | None,
    accounts: list[Account] | None,
    ignore: list[str] | None,
    balances: list[Balance] | None,
    test: bool = False,
) -> None:
    if test:
        test_flag = "test_"
    else:
        test_flag = ""
    last_month = (
        dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(months=1)
    ).strftime("%B")
    this_year = dt.datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y")
    shutil.copy2("Transactions.csv", f"{test_flag}{last_month}{this_year}Raw.csv")
    if accounts is not None:
        export_accounts(accounts, f"{test_flag}Accounts")
        print("Accounts saved as Accounts.csv")
    else:
        print("Accounts not imported")
    if transactions is not None:
        export_payments(transactions, f"{test_flag}{last_month} {this_year}.csv")
        print(f"Matched payments saved as {last_month} {this_year}.csv")
    else:
        print("Transactions not imported")
    if ignore is not None:
        export_words_to_ignore(ignore, f"{test_flag}WordsToIgnore")
        print("Words saved as WordsToIgnore.csv")
    else:
        print("Words To Ignore not imported")
    if balances is not None:
        export_balances(balances, f"{test_flag}Balances")
        print("Updated Balances saved as Balances.csv")
    else:
        print("Balances not imported")
    print("Files Saved")


def save_files_action(test: bool = False) -> None:
    transactions = state["transactions"]
    accounts = state["accounts"]
    ignore = state["words_to_ignore"]
    balance = state["balances"]
    save_files(transactions, accounts, ignore, balance, test)


def exit_program(test: bool = False) -> None:
    save_files_action(test)
    print("Exiting Program")
    sys.exit(0)


actions = {
    "Import Accounts & Balances": {
        "available": True,
        "function": import_accounts_and_balances_action,
    },
    "Import Banking Data": {"available": True, "function": import_banking_action},
    "Match Transactions to Accounts": {
        "available": False,
        "function": match_transactions_action,
    },
    "Proccess Payments": {"available": False, "function": process_payments_action},
    "Proccess Unknown Words": {
        "available": False,
        "function": procces_unknown_words_action,
    },
    "Save Files": {"available": True, "function": save_files_action},
    "Exit Program": {"available": True, "function": exit_program},
}

if __name__ == "__main__":

    args = start_program()
    while True:
        show_menu(args.test)
