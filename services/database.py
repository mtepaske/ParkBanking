import sqlite3

from models.account import Account
from models.balance import Balance, money
from models.transactions import Transaction
from services.settings import APP_DIRECTORY, get_setting

db_folder = APP_DIRECTORY / get_setting("db_path")
db_folder.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    """
    Establish the database connection

    Returns:
        The database connection
    """

    db_path = db_folder / "database.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    return connection


def disconnect(connection: sqlite3.Connection) -> None:
    """
    Close a database connection

    Args:
        connection: The connection to close
    """

    connection.close()


def initialise_database(connection: sqlite3.Connection) -> None:
    """
    Initialise an empty database with empty tables

    Args:
        connection: The database connection
    """

    with connection:

        # Accounts table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                site_number TEXT NOT NULL,
                name TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Ensure sites don't have two active accounts
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                unique_active_site_number
            ON accounts (site_number)
            WHERE active = 1
        """)

        # Balances table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL UNIQUE,
                annual TEXT NOT NULL,
                remaining TEXT NOT NULL,
                outstanding TEXT NOT NULL,
                credit TEXT NOT NULL,
                pay_frequency TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)

        # Words To Ignore table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ignore (
                word TEXT NOT NULL UNIQUE
            )
        """)

        # Aliases table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS aliases (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)

        # Payments table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                amount TEXT NOT NULL,
                details TEXT NOT NULL,
                particulars TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)


class Repository:
    """
    A repository used to query a database

    Attributes:
        connection: The database connection
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        """
        Initialises the instance

        Args:
            connection: The database connection
        """

        self.connection = connection

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a database query

        Args:
            query: The SQL query to execute
            parameters: The parameters of the query

        Returns:
            A cursor object
        """

        return self.connection.execute(query, parameters)

    def executemany(self, query: str, parameters: list[tuple]) -> sqlite3.Cursor:
        """
        Execute multiple database queries

        Args:
            query: The SQL query to execute
            parameters: The parameters of each query

        Returns:
            A cursor object
        """

        return self.connection.executemany(query, parameters)


class AccountRepository(Repository):
    """A repository specifically used to access account related information"""

    def get_all_accounts(self) -> list[Account]:
        """
        Get all accounts in the database

        Returns:
            A list of accounts
        """

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
        """
        Gets active accounts in the database

        Returns:
            A list of active accounts
        """

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
        """
        Get a balances from the database

        Args:
            account_id: The account ID of the balance to get

        Returns:
            The balance for the account

        Raises:
            RuntimeError: If the account ID has no connected balance in the database
        """

        balance_row = self.execute(
            """
            SELECT
                balances.id,
                balances.account_id,
                balances.annual,
                balances.remaining,
                balances.outstanding,
                balances.pay_frequency,
                balances.credit,
                accounts.site_number
            FROM balances 
            JOIN accounts
            ON balances.account_id = accounts.id
            WHERE accounts.id = ?
            """,
            (account_id,),
        ).fetchone()

        # If the account has no balance in the database
        if balance_row is None:
            raise RuntimeError(f"Account {account_id} has no associated balance")

        return Balance(
            account_id=balance_row["account_id"],
            site_number=balance_row["site_number"],
            annual=balance_row["annual"],
            remaining=balance_row["remaining"],
            outstanding=balance_row["outstanding"],
            pay_frequency=balance_row["pay_frequency"],
            credit=balance_row["credit"],
            balance_id=balance_row["id"],
        )

    def get_aliases(self, account_id: int) -> set[str]:
        """
        Get the aliases associated with an account from the database

        Args:
            account_id: The account ID of the aliases to get

        Returns:
            A set containing the aliases
        """

        alias_rows = self.execute(
            """
            SELECT alias 
            FROM aliases 
            WHERE account_id = ? 
            ORDER BY alias
            """,
            (account_id,),
        )

        return {row["alias"] for row in alias_rows}

    def get_history(self, account_id: int) -> list[Transaction]:
        """
        Get the history of associated with an account from the database

        Args:
            account_id: The account ID to get the history of

        Returns:
            A list of transactions that make up the history
        """

        payment_rows = self.execute(
            """
            SELECT *
            FROM payments
            WHERE account_id = ?
            ORDER BY date ASC
            """,
            (account_id,),
        )

        return [
            Transaction(
                date=row["date"],
                amount=money(row["amount"]),
                details=row["details"],
                type_str=row["particulars"],
                account_id=account_id,
                transaction_id=row["id"],
            )
            for row in payment_rows
        ]

    def save_accounts(self, accounts: list[Account]) -> dict[str, int]:
        """
        Save a list of accounts to the database

        Args:
            accounts: A list of accounts to save

        Returns:
            A dictionary containing the amount of new accounts added and accounts updated
        """

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
        """
        Save a single account to the database

        Args:
            account: The account to save

        Returns:
            True if the account wasnt already in the database

        Raises:
            ValueError: If the account to add has no balance connected to it, or if the account has an ID but isn't in the database
        """

        # If the account doesn't already exist in the database
        if account.account_id is None:

            # If the account to add has no balance
            if account.balance is None:
                raise ValueError(f"Account {account.account_id} has no balance")

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
            account.balance.account_id = account.account_id
            self._save_balance(account.balance)
            self._save_aliases(account)

            return True

        # If the account already exists in the database
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

            # If no account was updated
            if cursor.rowcount != 1:
                raise ValueError(
                    f"Account {account.account_id} does not exist in the database"
                )

            # If the account to add has no balance
            if account.balance is None:
                raise ValueError(f"Account {account.account_id} has no balance")

            account.balance.account_id = account.account_id
            self._save_balance(account.balance)
            self._save_aliases(account)

            return False

    def _save_aliases(self, account: Account) -> None:
        """
        Save the aliases associated with an account to the database

        Args:
            account: The account of the aliases to save
        """

        # Delete all the existing aliases for the account
        self.execute(
            """
            DELETE FROM aliases 
            WHERE account_id = ?
            """,
            (account.account_id,),
        )

        # Add all the aliases for the account
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
        """
        Save the balance information associated with an account

        Args:
            balance: The balance to save

        Raises:
            ValueError: If the balance has no account ID
        """

        # Check the balance has an account ID
        if balance.account_id is None:
            raise ValueError("Insert Failed. Balance has no account id")

        # If the balance doesn't already exist in the database
        if balance.balance_id is None:
            cursor = self.execute(
                """
                INSERT INTO balances (
                account_id, 
                annual, 
                remaining, 
                outstanding, 
                credit,
                pay_frequency
                ) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    balance.account_id,
                    str(balance.annual),
                    str(balance.remaining),
                    str(balance.outstanding),
                    str(balance.credit),
                    balance.pay_frequency,
                ),
            )
            balance.balance_id = cursor.lastrowid

        # If the balance already exists in the database
        else:
            cursor = self.execute(
                """
                UPDATE balances 
                SET annual = ?, 
                remaining = ?, 
                outstanding = ?, 
                credit = ?,
                pay_frequency = ? 
                WHERE id = ?
                """,
                (
                    str(balance.annual),
                    str(balance.remaining),
                    str(balance.outstanding),
                    str(balance.credit),
                    balance.pay_frequency,
                    balance.balance_id,
                ),
            )

            # If no balance was updated
            if cursor.rowcount != 1:
                raise ValueError(
                    f"Balance {balance.balance_id} does not exist in the database"
                )

    def save_history(self, history: list[Transaction]) -> None:
        """
        Save an account history to the database

        Args:
            history: A list of transactions to save
        """

        with self.connection:
            for payment in history:
                self._save_history_item(payment)

    def _save_history_item(self, history_item: Transaction) -> None:
        """
        Save a single history item to the database

        Args:
            history_item: The history item to save

        Raises:
            ValueError: If the history item has no account id
        """

        # If the history item has no attached account or account_id
        assert history_item.account is not None
        if history_item.account.account_id is None:
            raise ValueError(f"Insert Failed. {history_item} Has No Account ID")

        cursor = self.execute(
            """
            INSERT INTO payments (
            account_id,
            date,
            amount,
            details,
            particulars
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                history_item.account.account_id,
                history_item.date,
                str(history_item.amount),
                history_item.details,
                history_item.type,
            ),
        )

        # Add the database ID to the history item
        history_item.transaction_id = cursor.lastrowid

    def delete_history_item(self, history_item: Transaction) -> None:
        """
        Delete a history item from the database

        Args:
            history_item: The history item to delete

        Raises:
            ValueError: If the history item has no database ID
        """

        with self.connection:

            # If the history item has no database ID
            if history_item.transaction_id is None:
                raise ValueError(f"Delete Failed. {history_item} Has No Database ID")

            self.execute(
                """
                DELETE FROM payments
                WHERE id = ?
                """,
                (history_item.transaction_id,),
            )

    def delete_history_by_account(self, account: Account) -> None:
        """
        Delete the history associated with an account

        Args:
            account: The account to delete the history of

        Raises:
            ValueError: If the account has no database ID
        """

        with self.connection:

            # If the account has no database ID
            if account.account_id is None:
                raise ValueError(f"Delete Failed. {account} Has No Database ID")

            self.execute(
                """
                DELETE FROM payments
                WHERE account_id = ?
                """,
                (account.account_id,),
            )


class IgnoreRepository(Repository):
    """A repository specifically used to access words to ignore"""

    def get_all_ignore(self) -> set[str]:
        """
        Get all words to ignore in the database

        Returns:
            A set of words to ignore
        """

        return {row["word"] for row in self.execute("""
            SELECT * 
            FROM ignore
            """).fetchall()}

    def save_all_ignore(self, words: set[str]) -> None:
        """
        Save words to ignore to the database

        Args:
            words: A set of words to save
        """

        with self.connection:

            # Delete all existing words to ignore
            self.execute("""
                DELETE FROM ignore
                """)

            # Add the new words to ignore
            self.executemany(
                """
                INSERT INTO ignore 
                (word) VALUES (?)
                """,
                [(word,) for word in set(words)],
            )
