import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from textual.message_pump import Callback

from models.account import Account
from models.site import Site
from models.transactions import Transaction
from services.database import AccountRepository, IgnoreRepository
from services.settings import APP_DIRECTORY


def enable_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename=APP_DIRECTORY / "parkbanking_debug.log",
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
    charges: list[Transaction] = field(default_factory=list)
    # Refactor code to add charges to correct list
    unapplied: list[Transaction] = field(default_factory=list)
    sites: list[Site] = field(default_factory=list)

    _listeners: list[Callable] = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    def subscribe(self, callback: Callback):
        self._listeners.append(callback)

    def unsubscribe(self, callback: Callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def notify_changed(self):
        for callback in self._listeners.copy():
            callback()

    def add_account(self, account: Account):

        for old_account in self.accounts:
            if (
                account.site_number == old_account.site_number
                and account.active
                and old_account.active
            ):
                raise DuplicateAccount(
                    f"Account {old_account} Is Already Active For Site {old_account.site_number}"
                )

        self.accounts.append(account)
        self.notify_changed()

    def remove_account(self, account: Account):
        self.accounts.remove(account)
        self.notify_changed()

    def deactivate_by_site_number(self, site_number: str):
        for account in self.accounts:
            if account.site_number == site_number and account.active:
                account.switch_active()
                break

    def clear_accounts(self):
        self.accounts: list[Account] = []
        self.notify_changed()

    def add_transaction(self, transaction: Transaction):

        for old_transaction in self.transactions:
            if (
                transaction.date == old_transaction.date
                and transaction.amount == old_transaction.amount
                and transaction.details == old_transaction.details
            ):
                raise DuplicateTransaction(
                    f"Transaction {transaction} Is Already Loaded"
                )

        self.transactions.append(transaction)
        self.notify_changed()

    def remove_transaction(self, transaction: Transaction):
        self.transactions.remove(transaction)
        self.notify_changed()

    def clear_transactions(self):
        self.transactions: list[Transaction] = []
        self.notify_changed()

    def add_ignore(self, word: str):
        self.words_to_ignore.add(word)
        self.notify_changed()

    def remove_ignore(self, word: str):
        self.words_to_ignore.remove(word)
        self.notify_changed()

    def clear_ignore(self):
        self.words_to_ignore: set[str] = set()
        self.notify_changed()

    def add_unknown(self, word: str):
        self.unknown_words.add(word)
        self.notify_changed()

    def remove_unknown(self, word: str):
        self.unknown_words.remove(word)
        self.notify_changed()

    def clear_unknown(self):
        self.unknown_words: set[str] = set()
        self.notify_changed()

    def add_payment(self, payment: Transaction):

        for old_payment in self.payments:
            if (
                payment.date == old_payment.date
                and payment.amount == old_payment.amount
                and payment.details == old_payment.details
                and payment.account_id == old_payment.account_id
                and payment.account_id is not None
                or payment.date == old_payment.date
                and payment.amount == old_payment.amount
                and payment.details == old_payment.details
                and payment.account == old_payment.account
            ):
                raise DuplicateTransaction(f"Transaction {payment} Is Already Loaded")

        self.payments.append(payment)
        self.notify_changed()

    def remove_payment(self, payment: Transaction):
        self.payments.remove(payment)
        self.notify_changed()

    def clear_payments(self):
        self.payments: list[Transaction] = []
        self.notify_changed()

    def add_charge(self, charge: Transaction):

        assert charge.account is not None
        for old_charge in self.charges:
            if (
                charge.date == old_charge.date
                and charge.amount == old_charge.amount
                and charge.details == old_charge.details
                and charge.account_id == old_charge.account_id
                and charge.account_id is not None
                or charge.date == old_charge.date
                and charge.amount == old_charge.amount
                and charge.details == old_charge.details
                and charge.account == old_charge.account
            ):
                raise DuplicateTransaction(f"Transaction {charge} Is Already Loaded")

        self.charges.append(charge)
        self.notify_changed()

    def remove_charge(self, charge: Transaction):
        self.charges.remove(charge)
        self.notify_changed()

    def clear_charges(self):
        self.charges: list[Transaction] = []
        self.notify_changed()

    def add_unapplied(self, transaction: Transaction):
        self.unapplied.append(transaction)
        self.notify_changed()

    def apply_unapplied(self, transaction: Transaction):
        self.unapplied.remove(transaction)
        if transaction.amount > 0:
            self.add_payment(transaction)
        else:
            self.add_charge(transaction)
        self.notify_changed()

    def remove_unapplied(self, transaction: Transaction):
        self.unapplied.remove(transaction)
        self.notify_changed()

    def add_site(self, site: Site):
        self.sites.append(site)
        self.notify_changed()

    def remove_site(self, site: Site):
        self.sites.remove(site)
        self.notify_changed()

    def clear_sites(self):
        self.sites: list[Site] = []
        self.notify_changed()


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


class NoAccountID(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NoMatchingAccount(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class MissingBalance(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DuplicateAccount(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DuplicateTransaction(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
