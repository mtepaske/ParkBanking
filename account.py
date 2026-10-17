from __future__ import annotations

from balance import Balance


class Account:
    """Stores and manipulates Account information

    Attributes:
        id: (int) A unique identifier for database operations
        name: (str) Name of account holder
        site: (str) Site number
        aliases: (list[str]) Any keywords connected to the account, used for matching
        balance: (Balance) The account balance information
        active: (bool) The active status of this account
    """

    def __init__(
        self,
        site: str | int,
        name: str,
        aliases: list[str],
        account_id: int | None = None,
        active: bool = True,
    ) -> None:
        """Initialises Account object

        Args:
            site: (str) Site Number
            name: (str) Name of Site Holder
            aliases: (list[str]) Any keywords connected to the account
            account_id: (int | None) A unique identifier for database operations. Defaults to None if new account
            active: (bool) The active status of this account. Defaults to True

        Returns:
            None
        """
        self.id = account_id
        self.name = name
        self.site = site
        self.aliases = aliases
        if len(self.aliases) == 1:
            toadd = self.name.split(" ")
            toadd.append(str(site))
            toadd.append(toadd[0].upper())
            toadd.append(toadd[1].upper())
            self.aliases = toadd
        self.balance = None
        self.active = active

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Account:
        """Converts from csv row to an instance of the Account class

        Args:
            row: (dict[str, str]) A row of the csv file to convert

        Returns:
            (Account) An instanve of the account class
        """
        # Have to change for if there is no entry in rows to add active = 1 and account_id = None
        return cls(
            site=row["Site"],
            name=row["Name"],
            aliases=row["Aliases"].split(","),
            account_id=int(row["Account ID"]),
            active=bool(row["Active"]),
        )

    def add_balance(self, balance: Balance):
        self.balance = balance

    def add_alias(self, alias: str) -> bool:
        """Add a new alias to an account

        Args:
            alias: (str) Alias to add

        Returns:
            (bool) True if alias added, False If alias already connected
        """
        if alias in self.aliases:
            print(f"{alias} is already an alias for Site {self.site}")
            return False
        else:
            self.aliases.append(alias)
            print(f"{alias} added as alias for Site {self.site}")
            return True

    def to_dict(self) -> dict[str, str]:
        """Converts this instance of the Account class into a dictionary for exporting

        Returns:
            (dict[str, str]) A dictionary representing the account
        """
        return {
            "ID": str(self.id),
            "Name": self.name,
            "Site": str(self.site),
            "Aliases": ",".join(self.aliases),
            "Active": str(self.active),
        }

    def __str__(self) -> str:
        """Prints Account as string

        Returns:
            (str) A string representing the Account
        """
        return f"{self.site}: {self.name} --> {self.aliases}"
