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
                annual TEXT NOT NULL,
                remaining TEXT NOT NULL,
                outstanding TEXT NOT NULL,
                pay_period TEXT NOT NULL,
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
    def get_all(self) -> list[Account]:
        rows = self.connection.execute("""
            SELECT * 
            FROM accounts 
            ORDER BY site_number
            """).fetchall()
        return [
            Account(
                row["site_number"],
                row["name"],
                self.get_aliases(row["id"]),
                row["id"],
                row["active"],
            )
            for row in rows
        ]

    def get_active(self) -> list[Account]:
        rows = self.connection.execute("""
            SELECT * 
            FROM accounts 
            WHERE active = 1 
            ORDER BY site_number
            """).fetchall()
        return [
            Account(
                row["site_number"],
                row["name"],
                self.get_aliases(row["id"]),
                row["id"],
                row["active"],
            )
            for row in rows
        ]

    def get_aliases(self, account_id: int) -> list[str]:
        rows = self.connection.execute(
            """
            SELECT alias 
            FROM aliases 
            WHERE account_id = ? 
            ORDER BY alias
            """,
            (account_id,),
        )
        return [row["alias"] for row in rows]

    def insert_one(self, account: Account) -> None:
        with self.connection as connection:
            if account.id is None:
                cursor = connection.execute(
                    """
                    INSERT INTO accounts (
                    site_number, 
                    name, 
                    active
                    ) 
                    VALUES (?, ?, ?)
                    """,
                    (account.site, account.name, int(account.active)),
                )
                account.id = cursor.lastrowid
                connection.executemany(
                    """
                    INSERT INTO aliases (
                    account_id,
                    alias
                    )
                    VALUES (?, ?)
                    """,
                    [(account.id, alias) for alias in account.aliases],
                )
            else:
                connection.execute(
                    """
                    UPDATE accounts 
                    SET site_number = ?, 
                    name = ?, 
                    active = ? 
                    WHERE id = ?
                    """,
                    (account.site, account.name, account.active, account.id),
                )
                connection.execute(
                    """
                    DELETE FROM aliases
                    WHERE account_id = ?
                    """,
                    (account.id,),
                )
                connection.executemany(
                    """
                    INSERT INTO aliases (
                    account_id,
                    alias
                    )
                    VALUES (?, ?)
                    """,
                    [(account.id, alias) for alias in account.aliases],
                )

    def insert_all(self, accounts: list[Account]) -> None:
        with self.connection as connection:
            for account in accounts:
                if account.id is None:
                    cursor = connection.execute(
                        """
                        INSERT INTO accounts (
                        site_number, 
                        name, 
                        active
                        ) 
                        VALUES (?, ?, ?)
                        """,
                        (account.site, account.name, int(account.active)),
                    )
                    account.id = cursor.lastrowid
                    connection.executemany(
                        """
                        INSERT INTO aliases (
                        account_id,
                        alias
                        )
                        VALUES (?, ?)
                        """,
                        [(account.id, alias) for alias in account.aliases],
                    )
                else:
                    connection.execute(
                        """
                        UPDATE accounts 
                        SET 
                        site_number = ?, 
                        name = ?, 
                        active = ? 
                        WHERE id = ?
                        """,
                        (account.site, account.name, account.active, account.id),
                    )
                    connection.execute(
                        """
                        DELETE FROM aliases
                        WHERE account_id = ?
                        """,
                        (account.id,),
                    )
                    connection.executemany(
                        """
                        INSERT INTO aliases (
                        account_id,
                        alias
                        )
                        VALUES (?, ?)
                        """,
                        [(account.id, alias) for alias in account.aliases],
                    )

    def save_aliases(self, account: Account) -> None:
        with self.connection as connection:
            connection.execute(
                """
                DELETE FROM aliases 
                WHERE account_id = ?
                """,
                (account.id,),
            )

            connection.executemany(
                """
                INSERT INTO aliases (
                account_id, 
                alias
                )
                VALUES (?, ?)
                """,
                [(account.id, alias) for alias in account.aliases],
            )


class BalanceRepository(Repository):
    def get_all(self) -> list[Balance]:
        rows = self.connection.execute("""
            SELECT balances.*, accounts.site_number 
            FROM balances 
            JOIN accounts 
            ON balances.account_id = accounts.id
            ORDER BY account_id
            """)
        return [
            Balance(
                row["id"],
                row["account_id"],
                row["site_number"],
                row["annual"],
                row["remaining"],
                row["outstanding"],
                row["pay_period"],
            )
            for row in rows
        ]

    def get_active(self) -> list[Balance]:
        rows = self.connection.execute("""
            SELECT balances.*, accounts.site_number
            FROM balances 
            JOIN accounts 
            ON balances.account_id = accounts.id 
            WHERE accounts.active = 1
            ORDER BY accounts.site_number
            """).fetchall()
        return [
            Balance(
                row["id"],
                row["account_id"],
                row["site_number"],
                row["annual"],
                row["remaining"],
                row["outstanding"],
                row["pay_period"],
            )
            for row in rows
        ]

    def insert_one(self, balance: Balance) -> None:
        with self.connection as connection:
            if balance.id is None:
                cursor = connection.execute(
                    """
                    INSERT INTO balances (
                    account_id, 
                    annual, 
                    remaining, 
                    outstanding, 
                    pay_period) 
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
                connection.execute(
                    """
                    UPDATE balances 
                    SET account_id = ?, 
                    annual = ?, 
                    remaining = ?, 
                    outstanding = ?, 
                    pay_period = ? 
                    WHERE id = ?
                    """,
                    (
                        balance.account_id,
                        balance.annual,
                        balance.remaining,
                        balance.outstanding,
                        balance.pay_frequency,
                        balance.id,
                    ),
                )

    def insert_all(self, balances: list[Balance]) -> None:
        with self.connection as connection:
            for balance in balances:
                if balance.id is None:
                    cursor = connection.execute(
                        """
                        INSERT INTO balances (
                        account_id, 
                        annual, 
                        remaining, 
                        outstanding, 
                        pay_period) 
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
                    connection.execute(
                        """
                        UPDATE balances 
                        SET account_id = ?, 
                        annual = ?, 
                        remaining = ?, 
                        outstanding = ?, 
                        pay_period = ? 
                        WHERE id = ?
                        """,
                        (
                            balance.account_id,
                            balance.annual,
                            balance.remaining,
                            balance.outstanding,
                            balance.pay_frequency,
                            balance.id,
                        ),
                    )


class IgnoreRepository(Repository):
    def get_all(self) -> list[str]:
        return [row["word"] for row in self.execute("""
            SELECT * 
            FROM ignore
            """).fetchall()]

    def replace_all(self, words: list[str]) -> None:
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
