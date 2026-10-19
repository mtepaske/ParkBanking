from cli.matching import review_matches
from models.account import Account
from models.transactions import Transaction
from services.match import Matcher


def match_transactions(
    accounts: list[Account], transactions: list[Transaction], ignore: list[str]
) -> Matcher:
    """Matches transactions to accounts using the Matcher class

    Args:
        accounts: (list[Account]) A list of accounts to match to
        transactions: (list[Transaction]) A list of transactions to match
        ignore: (list[str]) A list of words to ignore

    Returns:
        (Matcher) The matcher used to match transactions to accounts
    """
    matcher = Matcher(accounts, ignore)
    for transaction in transactions:
        possibilities = matcher.keyword_match(transaction)
        matcher.match(transaction, possibilities)
    review_matches(transactions, accounts)
    return matcher


def process_payments(transactions: list[Transaction]) -> None:
    """Procces the matched transactions and update account balances

    Args:
        transactions: (list[Transaction]) A list of the matched transactions

    Returns:
        None
    """
    for transaction in transactions:
        if transaction.account is None:
            continue
        assert transaction.account.balance is not None
        transaction.account.balance.add_payment(transaction.amount)


def procces_unknown_words(matcher: Matcher) -> list[str]:
    """Proccess any unknown words from the matching process

    Args:
        matcher: (Matcher) The instance of the Matcher classes used

    Returns:
        None
    """
    matcher.unknown_words()
    ignore = matcher.ignore
    return ignore
