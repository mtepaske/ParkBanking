import sqlite3
from pathlib import Path

from models.account import Account
from models.balance import Balance

DB_PATH = Path(__file__).resolve().parent / "parkbanking.db"


def connect(db_path=DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def disconnect(connection: sqlite3.Connection) -> None:
    connection.close()


def initialise_database(connection: sqlite3.Connection) -> None:
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                site_number TEXT NOT NULL,
                name TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                unique_active_site_number
            ON accounts (site_number)
            WHERE active = 1
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL UNIQUE,
                annual TEXT NOT NULL,
                remaining TEXT NOT NULL,
                outstanding TEXT NOT NULL,
                pay_frequency TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ignore (
                word TEXT NOT NULL UNIQUE
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS aliases (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                UNIQUE (account_id, alias)
            )
        """)


class Repository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        return self.connection.execute(query, parameters)

    def executemany(self, query: str, parameters) -> sqlite3.Cursor:
        return self.connection.executemany(query, parameters)


class AccountRepository(Repository):
    def get_all_accounts(self) -> list[Account]:
        account_rows = self.execute("""
            SELECT * 
            FROM accounts 
            ORDER BY site_number
            """).fetchall()
        return [
            Account(
                site_number=row["site_number"],
                name=row["name"],
                balance=self.get_balance(row["id"]),
                aliases=self.get_aliases(row["id"]),
                account_id=row["id"],
                active=bool(row["active"]),
            )
            for row in account_rows
        ]

    def get_active_accounts(self) -> list[Account]:
        account_rows = self.execute("""
            SELECT * 
            FROM accounts 
            WHERE active = 1 
            ORDER BY site_number
            """).fetchall()
        return [
            Account(
                site_number=row["site_number"],
                name=row["name"],
                balance=self.get_balance(row["id"]),
                aliases=self.get_aliases(row["id"]),
                account_id=row["id"],
                active=bool(row["active"]),
            )
            for row in account_rows
        ]

    def get_balance(self, account_id: int) -> Balance:
        balance_row = self.execute(
            """
            SELECT
                balances.id,
                balances.account_id,
                balances.annual,
                balances.remaining,
                balances.outstanding,
                balances.pay_frequency,
                accounts.site_number
            FROM balances 
            JOIN accounts
            ON balances.account_id = accounts.id
            WHERE accounts.id = ?
            """,
            (account_id,),
        ).fetchone()
        if balance_row is None:
            raise RuntimeError(f"Account {account_id} has no associated balance")
        return Balance(
            account_id=balance_row["account_id"],
            site_number=balance_row["site_number"],
            annual=balance_row["annual"],
            remaining=balance_row["remaining"],
            outstanding=balance_row["outstanding"],
            pay_frequency=balance_row["pay_frequency"],
            id=balance_row["id"],
        )

    def get_all_balances(self) -> list[Balance]:
        balance_rows = self.execute("""
            SELECT balances.*, accounts.site_number 
            FROM balances 
            JOIN accounts 
            ON balances.account_id = accounts.id
            ORDER BY account_id
            """).fetchall()
        return [
            Balance(
                account_id=row["account_id"],
                site_number=row["site_number"],
                annual=row["annual"],
                remaining=row["remaining"],
                outstanding=row["outstanding"],
                pay_frequency=row["pay_frequency"],
                id=row["id"],
            )
            for row in balance_rows
        ]

    def get_active_balances(self) -> list[Balance]:
        balance_rows = self.execute("""
            SELECT balances.*, accounts.site_number
            FROM balances 
            JOIN accounts 
            ON balances.account_id = accounts.id 
            WHERE accounts.active = 1
            ORDER BY accounts.site_number
            """).fetchall()
        return [
            Balance(
                account_id=row["account_id"],
                site_number=row["site_number"],
                annual=row["annual"],
                remaining=row["remaining"],
                outstanding=row["outstanding"],
                pay_frequency=row["pay_frequency"],
                id=row["id"],
            )
            for row in balance_rows
        ]

    def get_aliases(self, account_id: int) -> list[str]:
        alias_rows = self.execute(
            """
            SELECT alias 
            FROM aliases 
            WHERE account_id = ? 
            ORDER BY alias
            """,
            (account_id,),
        )
        return [row["alias"] for row in alias_rows]

    def save_accounts(self, accounts: list[Account]) -> dict[str, int]:
        with self.connection:
            insert = 0
            update = 0
            for account in accounts:
                inserted = self._save_account(account)
                if inserted:
                    insert += 1
                else:
                    update += 1
        return {"Inserted": insert, "Updated": update}

    def _save_account(self, account: Account) -> bool:
        if account.account_id is None:
            cursor = self.execute(
                """
                INSERT INTO accounts (
                site_number, 
                name, 
                active
                ) 
                VALUES (?, ?, ?)
                """,
                (account.site_number, account.name, int(account.active)),
            )
            account.account_id = cursor.lastrowid
            if account.balance is None:
                raise ValueError(f"Account {account.account_id} has no balance")
            account.balance.account_id = account.account_id
            self._save_balance(account.balance)
            self._save_aliases(account)
            return True
        else:
            cursor = self.execute(
                """
                UPDATE accounts 
                SET site_number = ?, 
                name = ?, 
                active = ? 
                WHERE id = ?
                """,
                (
                    account.site_number,
                    account.name,
                    int(account.active),
                    account.account_id,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError(
                    f"Account {account.account_id} does not exist in the database"
                )
            if account.balance is None:
                raise ValueError(f"Account {account.account_id} has no balance")
            account.balance.account_id = account.account_id
            self._save_balance(account.balance)
            self._save_aliases(account)
            return False

    def _save_aliases(self, account: Account) -> None:
        self.execute(
            """
            DELETE FROM aliases 
            WHERE account_id = ?
            """,
            (account.account_id,),
        )
        self.executemany(
            """
            INSERT INTO aliases (
            account_id, 
            alias
            )
            VALUES (?, ?)
            """,
            [(account.account_id, alias) for alias in account.aliases],
        )

    def _save_balance(self, balance: Balance) -> None:
        if balance.account_id is None:
            raise ValueError("Insert Failed. Balance has no account id")
        if balance.id is None:
            cursor = self.execute(
                """
                INSERT INTO balances (
                account_id, 
                annual, 
                remaining, 
                outstanding, 
                pay_frequency) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    balance.account_id,
                    balance.annual,
                    balance.remaining,
                    balance.outstanding,
                    balance.pay_frequency,
                ),
            )
            balance.id = cursor.lastrowid
        else:
            cursor = self.execute(
                """
                UPDATE balances 
                SET annual = ?, 
                remaining = ?, 
                outstanding = ?, 
                pay_frequency = ? 
                WHERE id = ?
                """,
                (
                    balance.annual,
                    balance.remaining,
                    balance.outstanding,
                    balance.pay_frequency,
                    balance.id,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Balance {balance.id} does not exist in the database")


class IgnoreRepository(Repository):
    def get_all_ignore(self) -> list[str]:
        return [row["word"] for row in self.execute("""
            SELECT * 
            FROM ignore
            """).fetchall()]

    def replace_all_ignore(self, words: list[str]) -> None:
        with self.connection:
            self.execute("""
                DELETE FROM ignore
                """)
            self.executemany(
                """
                INSERT INTO ignore 
                (word) VALUES (?)
                """,
                [(word,) for word in set(words)],
            )
