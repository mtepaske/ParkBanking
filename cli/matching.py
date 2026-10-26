from rich.console import Console
from rich.table import Table

from cli.accounts_menu import account_picker
from models.account import Account
from models.transactions import Transaction


def review_matches(transactions: list[Transaction], accounts: list[Account]) -> None:
    """
    Displays and confirms an overview of matched/unmatched transactions after matching

    Args:
        transactions: A list of transactions that have been through the matcher
        accounts: A list of accounts that could have been matched agaisnt
    """

    console = Console()

    # Matched transactions appear green. Unmatched appear red
    matched = "green"
    no_match = "red"

    # Makes the display table
    table = Table(show_lines=True)
    table.add_column("Index")
    table.add_column("Date")
    table.add_column("Amount")
    table.add_column("Details")
    table.add_column("->")
    table.add_column("Account Site Number")
    table.add_column("Account Name")

    while True:

        index = 1
        for transaction in transactions:
            account = transaction.account

            # If transaction is matched to an account
            if account is None:
                table.add_row(
                    f"[blue]{index}[/blue]",
                    f"[{no_match}]{transaction.date}[/{no_match}]",
                    f"[{no_match}]${transaction.amount:,.2f}[/{no_match}]",
                    f"[{no_match}]{transaction.original_details}[/{no_match}]",
                    f"[{no_match}]->[/{no_match}]",
                    f"[{no_match}]?[/{no_match}]",
                    f"[{no_match}]?[/{no_match}]",
                )

            # If transaction is not matched to an account
            else:
                table.add_row(
                    f"[blue]{index}[/blue]",
                    f"[{matched}]{transaction.date}[/{matched}]",
                    f"[{matched}]${transaction.amount:,.2f}[/{matched}]",
                    f"[{matched}]{transaction.original_details}[/{matched}]",
                    f"[{matched}]->[/{matched}]",
                    f"[{matched}]{account.site_number}[/{matched}]",
                    f"[{matched}]{account.name}[/{matched}]",
                )
            index += 1

        # Display the table and ask for input
        console.print(table)
        choice = input("Are all the transactions matched correctly? (y/n): ")

        # Exit the screen if matches are correct
        if choice == "y":
            print("Transactions matched successfully")
            return

        # If incorrect, prompt user to slter the match
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
    """
    Change the account that a transaction is matched too

    Args:
        transaction: The transaction to change
        accounts: The list of accounts that could be changed too
    """

    # Display accounts for selection
    choice = account_picker(accounts)

    # If transaction matches no account, remove the current match
    if choice is None:
        transaction.account = None
        return

    # Add the user choice
    transaction.account = choice


def no_matches(accounts: list[Account], transaction: Transaction) -> None:
    """
    Allow the user to manualy choose the account to match too

    Args:
        accounts: The list of accounts to choose from
        transaction: The transaction to match
    """

    # Display the transaction and the possible accounts
    print(
        f"Date: {transaction.date}, Amount: {transaction.amount}, Details: {transaction.original_details}"
    )
    choice = account_picker(accounts)

    # If transaction matches no account
    if choice is None:
        return

    # Prompts the user for a choice of description
    while True:
        print("[1] -> Direct Debit")
        print("[2] -> Credit Card")
        print("[3] -> No Description")
        particulars = input("Enter Description Choice: ")
        if particulars == "1":
            transaction.type = "Direct Debit"
            break
        elif particulars == "2":
            transaction.type = "Credit Card"
            break
        elif particulars == "3":
            break
    transaction.account = choice


def match_to_account(
    transaction: Transaction,
    possibilities: list[Account],
    accounts: list[Account],
) -> None:
    """
    Match a transaction to an account based on a list of possibilities

    Args:
        transaction: The transaction to match
        possibilities: A list of possible matches
        accounts: The list of all possible accounts
    """

    # If no possibilities were found, user selects from all accounts
    if len(possibilities) == 0:
        print("\nNo Possible Matches Found")
        no_matches(accounts, transaction)

    # If one possibility, then add the account to the transaction
    elif len(possibilities) == 1:
        transaction.account = possibilities[0]
        transaction.type = "Direct Debit"
        print(f"Match found: {possibilities[0]}")

    # If multiple possibilities were found, user selects from possibilities
    else:
        amount = len(possibilities)
        print(f"\n{amount} Possible Choices Found")
        print(
            f"Date: {transaction.date}, Amount: {transaction.amount}, Details: {transaction.original_details}"
        )
        choice = account_picker(possibilities)
        if choice is None:
            return
        transaction.account = choice
        transaction.type = "Direct Debit"


def alias_handler(accounts: list[Account], alias: str) -> None:
    """
    Adds an alias to a user selected account

    Args:
        accounts: A list of loaded accounts
        alias: The alias to add
    """

    choice = account_picker(accounts)

    # If alias doesn't belong to any account
    if choice is None:
        return
    choice.add_alias(alias)


def ignore_handler(ignored: set[str], word: str) -> None:
    """
    Adds a word to the list of ignored words

    Args:
        ignored: The list of currently loaded words to ignore
        word: The word to add
    """

    ignored.add(word)


def unknown_words(
    accounts: list[Account], unknown: set[str], ignored: set[str]
) -> set[str]:
    """
    Prompts the user for choice for unknown words generated during matching

    Args:
        accounts: The list of loaded accounts
        unknown: The list of unknown words
        ignored: The list of loaded ignored words

    Returns:
        A set containing words that are still unknown
    """

    remove = []
    for word in unknown:

        # Displays the word and the available options
        while True:
            print(f"{word} is an unknown word, what would you like to do with it?")
            choice = input(
                "[i] - Add to ignored words\n"
                "[a] - Add as an alias\n"
                "[s] - skip\n"
                "What is your choice?: "
            )

            # Adds a word to ignored words
            if choice == "i":
                ignore_handler(ignored, word)
                remove.append(word)
                print(f"{word} Added to ignored words")
                break

            # Adds a word as an alias for an account
            elif choice == "a":
                alias_handler(accounts, word)
                remove.append(word)
                break

            # Skips over word
            elif choice == "s":
                break

            else:
                print("Choice invalid, please try again")

    # Removes handled words from unknown words
    for word in remove:
        unknown.remove(word)
    return unknown
