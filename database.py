import sqlite3

from account import Account
from balance import Balance


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
                site TEXT NOT NULL,
                annual TEXT NOT NULL,
                remaining TEXT NOT NULL,
                outstanding TEXT NOT NULL,
                pay_period TEXT NOT NULL,
                FEREIGN KEY (account_id) REFRENCES accounts(id)
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
                account_id INETGER NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (account_id) REFRENCES accounts(id)
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
    def get_all(self):
        with self.connection as connection:
            rows = connection.execute(
                "SELECT * FROM accounts ORDER BY site_number"
            ).fetchall()
        return [
            Account(row["site_number"], row["name"], None, row["id"]) for row in rows
        ]

    def get_aliases(self):
        pass

    def insert_one(self, account: Account):
        with self.connection as connection:
            if account.id is None:
                cursor = connection.execute(
                    "INSERT INTO accounts (site_number, name, active) VALUES (?, ?, ?)",
                    (account.site, account.name, int(account.active)),
                )
                account.id = cursor.lastrowid
            else:
                connection.execute(
                    "UPDATE accounts SET site_number = ?, name = ?, active = ? WHERE id = ?",
                    (account.site, account.name, account.active, account.id),
                )

    def insert_all(self, accounts: list[Account]):
        with self.connection as connection:
            for account in accounts:
                if account.id is None:
                    cursor = connection.execute(
                        "INSERT INTO accounts (site_number, name, active) VALUES (?, ?, ?)",
                        (account.site, account.name, int(account.active)),
                    )
                    account.id = cursor.lastrowid
                else:
                    connection.execute(
                        "UPDATE accounts SET site_number = ?, name = ?, active = ? WHERE id = ?",
                        (account.site, account.name, account.active, account.id),
                    )

    def save_aliases(self, account: Account):
        with self.connection as connection:
            connection.execute(
                "DELETE FROM aliases WHERE account_id = ?",
                (account.id,),
            )

            connection.executemany(
                """
                INSERT INTO aliases (account_id, alias),
                VALUES (?, ?)
            """,
                [(account.id, alias) for alias in account.aliases],
            )


class BalanceRepository(Repository):
    def get_all(self):
        return self.execute("SELECT * FROM balance").fetchall()

    def save(self, balances: list[Balance]):
        pass


class IgnoreRepository(Repository):
    def get_all(self):
        return [row["word"] for row in self.execute("SELECT * FROM ignore").fetchall()]

    def replace_all(self, words: list[str]):
        with self.connection:
            self.execute("DELETE FROM ignore")
            self.executemany(
                "INSERT INTO ignore (word) VALUES (?)", [(word,) for word in set(words)]
            )


class AliasRepository(Repository):
    def get_all(self):
        return self.execute("SELECT * FROM alias").fetchall()
