import logging
from dataclasses import dataclass, field

from models.account import Account
from models.transactions import Transaction
from services.database import AccountRepository, IgnoreRepository


def enable_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename="/.parkbanking/parkbanking_debug.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logger


@dataclass
class AppState:
    """
    Tracks the information state of the application

    Attributes:
        accounts: (list[Account]) A list of loaded accounts
        transactions: (list[Transaction]) A list of loaded unmatched/unapplied transactions
        words_to_ignore: (list[str]) A list of loaded words to ignore
        unknown_words: (set[str) A set of unknonw words generated during matching
        payments: (list[Transaction]) A list of applied payments
    """

    # Assign empty lists/sets
    accounts: list[Account] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    words_to_ignore: set[str] = field(default_factory=set)
    unknown_words: set[str] = field(default_factory=set)
    payments: list[Transaction] = field(default_factory=list)


@dataclass
class AppRepositories:
    """
    The repositories used for database queries

    Attributes:
        account_repo: (AccountRepository) The account repository
        ignore_repo: (IgnoreRepository) The words to ignore repository
    """

    account_repo: AccountRepository
    ignore_repo: IgnoreRepository


class Application:
    """
    Used to store and access current loaded information

    Attributes:
        repos: (AppRepositories) The database repositories
        state: (AppState) The current loaded information
    """

    def __init__(self, repos: AppRepositories) -> None:
        """
        Initialises the instance

        Args:
            repos: The repositories to use
        """

        self.repos = repos
        self.state = AppState()

    def load_from_db(self):
        self.state.accounts = self.repos.account_repo.get_active_accounts()
        self.state.words_to_ignore = self.repos.ignore_repo.get_all_ignore()

    def append_accounts(self, accounts_to_add: list[Account]) -> None:
        """
        Add new accounts to current loaded list

        Args:
            accounts_to_add: A list of accounts to add

        Raises:
            ValueError: If a new account conflicts with an account already loaded
        """

        for new_account in accounts_to_add:
            for old_account in self.state.accounts:
                if (
                    new_account.site_number == old_account.site_number
                    and new_account.active
                    and old_account.active
                ):
                    raise ValueError(
                        f"Account {old_account} Is Already Active For Site {old_account.site_number}"
                    )
            self.state.accounts.append(new_account)

    def append_words_to_ignore(self, words_to_add: list[str]) -> None:
        """
        Add new words to current loaded set

        Args:
            words_to_add: A list of words to add
        """

        for new_word in words_to_add:
            self.state.words_to_ignore.add(new_word)

    def append_transactions(self, transactions_to_add: list[Transaction]) -> None:
        """
        Add new transactions to current loaded list

        Args:
            transactions_to_add: A list of transactions to add

        Raises:
            ValueError: If a new transaction is the same as an already loaded transaction
        """

        for new_transaction in transactions_to_add:
            for old_transaction in self.state.transactions:
                if (
                    new_transaction.date == old_transaction.date
                    and new_transaction.amount == old_transaction.amount
                    and new_transaction.details == old_transaction.details
                ):
                    raise ValueError(f"Transaction {new_transaction} Is Already Loaded")
