from __future__ import annotations

from models.balance import Balance
from services.user import get_input


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

    aliases: list[str]

    def __init__(
        self,
        site: str | int,
        name: str,
        aliases: list[str] | None = None,
        account_id: int | None = None,
        active: bool = True,
    ) -> None:
        """Initialises Account object

        Args:
            site: (str) Site Number
            name: (str) Name of Site Holder
            aliases: (list[str] | None) Any keywords connected to the account. Defaults to None
            account_id: (int | None) A unique identifier for database operations. Defaults to None if new account
            active: (bool) The active status of this account. Defaults to True

        Returns:
            None
        """
        self.id = account_id
        self.name = name
        self.site = str(site)
        if len(self.site) == 1:
            self.site = f"0{self.site}"
        self.aliases = aliases if aliases is not None else []
        if len(self.aliases) == 0:
            names = self.name.split(" ")
            for alias in names:
                self.aliases.append(alias)
                self.aliases.append(alias.upper())
            self.aliases.append(self.site)
            self.aliases.append(str(site))
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
        if row["Active"] == "1" or row["Active"] == "None" or row["Active"] == "True":
            active = True
        else:
            active = False
        if row["ID"] == "None":
            return cls(
                site=row["Site"],
                name=row["Name"],
                aliases=row["Aliases"].split(","),
                account_id=None,
                active=active,
            )
        else:
            return cls(
                site=row["Site"],
                name=row["Name"],
                aliases=row["Aliases"].split(","),
                account_id=int(row["ID"]),
                active=active,
            )

    def add_balance(self, balance: Balance) -> None:
        """Adds a balance to the account

        Args:
            balance: (Balance) The balance to add

        Returns:
            None
        """
        self.balance = balance
        if self.id is not None:
            self.balance.account_id = self.id

    def change_site(self, new_site: str | None = None) -> None:
        """Changes the site number

        Args:
            new_site: (str | None) New site number to change to. If None is given prompts user for input

        Returns:
            None
        """
        if new_site is None:
            while True:
                try:
                    new_site = get_input("Enter new site number")
                    int(new_site)
                    break
                except ValueError:
                    print("Must enter number")
        old_site = self.site
        self.site = new_site
        self.aliases.append(new_site)
        if self.balance is not None:
            self.balance.change_site(new_site)
        print(f"Site number for {self.name} changed from {old_site} to {self.site}")

    def change_name(self, new_name: str | None = None) -> None:
        """Changes the name of the account

        Args:
            new_name: (str | None) New name to change to. If None is given prompts user for input

        Returns:
            None
        """
        if new_name is None:
            while True:
                new_name = get_input("Enter new name")
                break
        old_name = self.name
        self.name = new_name
        new_name_split = new_name.split(" ")
        for name in new_name_split:
            self.aliases.append(name)
            self.aliases.append(name.upper())
        print(f"Name for site {self.site} changed from {old_name} to {self.name}")

    def switch_active(self) -> None:
        """Switches the active status of the account

        Returns:
            None
        """
        if self.active is False:
            old_active = self.active
            self.active = True
        else:
            old_active = self.active
            self.active = False
        print(f"Active switched from {old_active} to {self.active}")

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
        if self.active == True:
            active = "1"
        else:
            active = "0"
        return {
            "ID": str(self.id),
            "Name": self.name,
            "Site": str(self.site),
            "Aliases": ",".join(self.aliases),
            "Active": active,
        }

    def __str__(self) -> str:
        """Prints Account as string

        Returns:
            (str) A string representing the Account
        """
        return f"{self.site}: {self.name} --> {self.aliases}"
