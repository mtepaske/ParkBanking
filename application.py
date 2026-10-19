from dataclasses import dataclass, field

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction
from services.database import AccountRepository, BalanceRepository, IgnoreRepository
from services.imports import import_words_to_ignore
from services.match import Matcher


@dataclass
class AppState:
    accounts: list[Account] = field(default_factory=list)
    balances: list[Balance] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    words_to_ignore: list[str] = field(default_factory=list)
    matcher: Matcher | None = None


@dataclass
class AppRepositories:
    account_repo: AccountRepository
    balance_repo: BalanceRepository
    ignore_repo: IgnoreRepository


class Application:
    def __init__(self, repos: AppRepositories) -> None:
        self.repos = repos
        self.state = AppState()

    def load_from_db(self) -> None:
        accounts = self.repos.account_repo.get_active()
        balances = self.repos.balance_repo.get_active()
        for account in accounts:
            for balance in balances:
                if account.id == balance.account_id:
                    account.add_balance(balance)
                    break
            if account.balance is None:
                print(
                    f"Could not find matching balance for {account}\nAssigning default balance"
                )
                balance = Balance(account.id, account.site, "7550", "7550", "0", "m")
                balances.append(balance)
                account.add_balance(balance)
        ignore = self.repos.ignore_repo.get_all()
        if len(ignore) == 0:
            print("Ignore Repository is Empty. Importing From CSV")
            ignore = import_words_to_ignore("WordsToIgnore.csv")
        self.state.accounts = accounts
        self.state.balances = balances
        self.state.words_to_ignore = ignore
        print("Accounts loaded")

    def save_to_db(self) -> None:
        self.repos.account_repo.insert_all(self.state.accounts)
        print("Accounts Successfully Inserted")
        self.repos.balance_repo.insert_all(self.state.balances)
        print("Balances Successfully Interted")
        if self.state.words_to_ignore is not None:
            self.repos.ignore_repo.replace_all(self.state.words_to_ignore)
            print("Words To Ignore Successfully Inserted")
