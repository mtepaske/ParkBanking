from dataclasses import dataclass, field

from models.account import Account
from models.transactions import Transaction
from services.database import AccountRepository, IgnoreRepository


@dataclass
class AppState:
    accounts: list[Account] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    words_to_ignore: list[str] = field(default_factory=list)
    unknown_words: list[str] = field(default_factory=list)
    payments: list[Transaction] = field(default_factory=list)
    # all_accounts: list[Account] = field(default_factory=list)


@dataclass
class AppRepositories:
    account_repo: AccountRepository
    ignore_repo: IgnoreRepository


class Application:
    def __init__(self, repos: AppRepositories) -> None:
        self.repos = repos
        self.state = AppState()

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
