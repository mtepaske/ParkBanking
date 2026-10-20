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
