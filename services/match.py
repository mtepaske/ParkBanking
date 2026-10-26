from decimal import Decimal

from models.account import Account
from models.balance import Balance, money
from models.transactions import Transaction


class Matcher:
    """
    Used to match transactions to accounts and store information for and generated during matching

    Attributes:
        accounts: (list[Account]) A list of accounts to match too
        ignore: (list[str]) A list of words to ignore during matching
        unknown: (set[str]) A list of unknown words encountered during matching
    """

    def __init__(self, accounts: list[Account], ignore: set[str]) -> None:
        self.accounts = accounts
        self.ignore = ignore
        self.unknown = set()

    def clean_desc(self, description: list[str]) -> list[str]:
        """
        Cleans a transactions description and removes ignored words

        Args:
            description: The description to clean

        Returns:
            A list of words not including ignored words
        """

        filtered = []
        for word in description:
            if word not in self.ignore:
                filtered.append(word)
        return filtered

    def keyword_match(self, transaction: Transaction) -> list[Account]:
        """
        Generates a list of possible matches based on if any details match any account aliases

        Args:
            transaction: The transaction to match

        Returns:
            A set of possible matches
        """
        possible = set()
        details = self.clean_desc(transaction.details)
        for word in details:
            found = False
            for account in self.accounts:
                if word in account.aliases:
                    found = True
                    possible.add(account)
            if not found:
                self.unknown.add(word)
        return list(possible)


def match_transactions(
    matcher: Matcher, transaction: Transaction
) -> list[Account]:  # Implimented for possible addition of extra matching methods
    """
    Uses a matcher instance to match a transaction to a list of possible accounts

    Args:
        matcher: An instance of matcher
        transaction: A transaction to match

    Returns:
        the possible matches
    """

    possibilities = matcher.keyword_match(transaction)
    return possibilities


def review_payment(
    balance: Balance, amount: Decimal
) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    """
    Calculates the balance before and after a payment or charge is applied for review purposes

    Args:
        balance: The balance to review
        amount: The amount to apply

    Returns:
        A tuple containing the old values and the new values calculated

    Raises:
        ValueError: If the amount is less then 0
    """

    # Sets the current balances
    new_remaining = balance.remaining
    new_outstanding = balance.outstanding
    new_credit = balance.credit

    # Normalises the amount as money
    amount = money(amount)

    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    # Applies the amount to outstanding fees first
    if amount < new_outstanding:
        new_outstanding -= amount

    # Then applies to remaining fees
    elif amount < balance.balance:
        amount -= new_outstanding
        new_outstanding = Decimal("0.00")
        new_remaining -= amount

    # Any remaining amount becomes credit
    else:
        amount -= new_outstanding
        new_outstanding = Decimal("0.00")
        amount -= new_remaining
        new_remaining = Decimal("0.00")
        new_credit = amount

    # Constructs a dictionary containing the old and new balances
    old_v_new = (
        {
            "Remaining": balance.remaining,
            "Outstanding": balance.outstanding,
            "Credit": balance.credit,
        },
        {
            "Remaining": new_remaining,
            "Outstanding": new_outstanding,
            "Credit": new_credit,
        },
    )
    return old_v_new
