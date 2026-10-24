from dataclasses import dataclass, field

from models.account import Account
from models.transactions import Transaction
from services.database import AccountRepository, IgnoreRepository
from services.imports import import_words_to_ignore


@dataclass
class AppState:
    accounts: list[Account] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    words_to_ignore: list[str] = field(default_factory=list)
    unknown_words: list[str] = field(default_factory=list)
    # all_accounts: list[Account] = field(default_factory=list)


@dataclass
class AppRepositories:
    account_repo: AccountRepository
    ignore_repo: IgnoreRepository


class Application:
    def __init__(self, repos: AppRepositories) -> None:
        self.repos = repos
        self.state = AppState()

    def load_from_db(self) -> bool:
        accounts = self.repos.account_repo.get_active_accounts()
        ignore = self.repos.ignore_repo.get_all_ignore()
        if len(ignore) == 0:
            print("Ignore Repository is Empty. Importing From CSV")
            ignore = import_words_to_ignore("WordsToIgnore.csv")
        self.state.accounts = accounts
        self.state.words_to_ignore = ignore
        return True

    def save_to_db(self) -> None:
        self.repos.account_repo.save_accounts(self.state.accounts)
        if self.state.words_to_ignore is not None:
            self.repos.ignore_repo.replace_all_ignore(self.state.words_to_ignore)

    def append_accounts(self, accounts_to_add: list[Account]) -> None:
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
        for new_word in words_to_add:
            for old_word in self.state.words_to_ignore:
                if new_word == old_word:
                    continue
            self.state.words_to_ignore.append(new_word)

    def append_transactions(self, transactions_to_add: list[Transaction]) -> None:
        for new_transaction in transactions_to_add:
            for old_transaction in self.state.transactions:
                if (
                    new_transaction.date == old_transaction.date
                    and new_transaction.amount == old_transaction.amount
                    and new_transaction.details == old_transaction.details
                ):
                    raise ValueError(f"Transaction {new_transaction} Is Already Loaded")
