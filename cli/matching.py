from rich.console import Console
from rich.table import Table

from cli.accounts_menu import account_picker
from models.account import Account
from models.transactions import Transaction


def review_matches(transactions: list[Transaction], accounts: list[Account]) -> None:
    console = Console()
    matched = "green"
    no_match = "red"
    while True:
        index = 1
        table = Table()
        table.add_column("Index")
        table.add_column("Date")
        table.add_column("Amount")
        table.add_column("Details")
        table.add_column("")
        table.add_column("Account Site Number")
        table.add_column("Account Name")
        for transaction in transactions:
            account = transaction.account
            if account is None:
                table.add_row(
                    f"[{no_match}]{index}[/{no_match}]",
                    f"[{no_match}]{transaction.date}[/{no_match}]",
                    f"[{no_match}]${transaction.amount:,.2f}[/{no_match}]",
                    f"[{no_match}]{transaction.details}[/{no_match}]",
                    f"[{no_match}]->[/{no_match}]",
                    f"[{no_match}]?[/{no_match}]",
                    f"[{no_match}]?[/{no_match}]",
                )
            else:
                table.add_row(
                    f"[{matched}]{index}[/{matched}]",
                    f"[{matched}]{transaction.date}[/{matched}]",
                    f"[{matched}]${transaction.amount:,.2f}[/{matched}]",
                    f"[{matched}]{transaction.details}[/{matched}]",
                    f"[{matched}]->[/{matched}]",
                    f"[{matched}]{account.site_number}[/{matched}]",
                    f"[{matched}]{account.name}[/{matched}]",
                )
            index += 1
        console.print(table)
        choice = input("Are all the transactions matched correctly? (y/n): ")
        if choice == "y":
            print("Transactions matched successfully")
            return
        elif choice == "n":
            while True:
                match_to_change = int(input("Which match?: "))
                try:
                    transaction_to_change = transactions[match_to_change - 1]
                    change_match(transaction_to_change, accounts)
                    break
                except (IndexError, KeyError):
                    print("Must choose from the available indexes")
        else:
            print("Please choose y or n")


def change_match(transaction: Transaction, accounts: list[Account]) -> None:
    choice = account_picker(accounts)
    if choice is None:
        return
    transaction.add_account(choice)
    print(transaction.account)


def no_matches(accounts: list[Account], transaction: Transaction) -> None:
    print(
        f"Date: {transaction.date}, Amount: {transaction.amount}, Details: {transaction.details}"
    )
    print("Which Account does this payment belong to?: ")
    choice = account_picker(accounts)
    if choice is None:
        return
    transaction.add_account(choice)


def match_to_account(
    transaction: Transaction,
    possibilities: list[Account],
    accounts: list[Account],
) -> None:
    if len(possibilities) == 0:
        print("No Possible Matches Found")
        no_matches(accounts, transaction)
    elif len(possibilities) == 1:
        transaction.add_account(possibilities[0])
        print(f"Match found: {possibilities[0]}")
    else:
        amount = len(possibilities)
        print(f"Details: {transaction.details}")
        print(f"{amount} Possible Choices Found")
        choice = account_picker(possibilities)
        if choice is None:
            return
        transaction.add_account(choice)


def alias_handler(accounts: list[Account], alias: str) -> None:
    choice = account_picker(accounts)
    if choice is None:
        return
    choice.add_alias(alias)


def ignore_handler(ignored: list[str], word: str) -> None:
    ignored.append(word)


def unknown_words(
    accounts: list[Account], unknown: list[str], ignored: list[str]
) -> None:
    for word in unknown:
        print(f"{word} is an unknown word, what would you like to do with it?")
        while True:
            choice = input(
                "[i] - Add to ignored words\n"
                "[a] - Add as an alias\n"
                "[s] - skip\n"
                "What is your choice?: "
            )
            if choice in ["i", "a", "s"]:
                break
            print("Choice invalid, please try again")
        if choice == "i":
            ignore_handler(ignored, word)
            print(f"{word} Added to ignored words")
        elif choice == "a":
            alias_handler(accounts, word)
