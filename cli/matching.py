from cli.menu import get_input
from models.account import Account
from models.transactions import Transaction
from services.match import Matcher


def review_matches(transactions: list[Transaction], accounts: list[Account]) -> None:
    """Prints a list of matched transactions and the matched accounts for proofing

    Args:
        matcher: (Matcher) The instance of matcher used to match transactions to accounts
        transactions: (list[Transaction]) The list of transactions to review
        accounts: (list[Accounts]) The list of accounts that could be matched against

    Returns:
        None
    """
    index = 1
    while True:
        for transaction in transactions:
            if transaction.account is None:
                print(f"[{index}] - No Match -> {transaction}")
            else:
                account = transaction.account
                print(f"[{index}] - {account.site}: {account.name} -> {transaction}")
            index += 1
        while True:
            choice = get_input("Are all the transactions matched correctly? (y/n)")
            if choice == "y":
                print("Transactions matched successfully")
                return
            elif choice == "n":
                while True:
                    match_to_change = int(get_input("Which match?"))
                    try:
                        transaction_to_change = transactions[match_to_change - 1]
                        Matcher.change_match(transaction_to_change, accounts)
                        break
                    except (IndexError, KeyError):
                        print("Must choose from the available indexes")
            else:
                print("Please choose y or n")
