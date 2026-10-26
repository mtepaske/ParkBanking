from __future__ import annotations

from models.balance import Balance


class Account:
    """
    Tracks account information


    Attributes:
        account_id: (int) The ID used for database queries. Gets assigned on first insertion to database
        name: (str) The name of the primary site holder
        balance: (Balance) The balance connected to the account. Should be assigned at or soon after initialisation
        active: (bool) The active status of the account
        site_number: (str) The site number for the account
        aliases: (list[str]) A list of keywords to match agaisnt
    """

    aliases: list[str]

    def __init__(
        self,
        site_number: str | int,
        name: str,
        balance: Balance | None = None,
        aliases: list[str] | None = None,
        account_id: int | None = None,
        active: bool = True,
    ) -> None:
        """
        Initialises the instance

        Args:
            site_number: The site number for the account. Nomarlisation occures to ensure it is always 2 digits
            name: The name of the primary site holder
            balance: The balance connected to the account
            aliases: A list of keywords to match agaisnt. If empty will construct a list from the name and site number
            account_id: The ID used for database queries. Gets assigned on first insertion to database
            active: The active status of the account
        """

        self.account_id = account_id
        self.name = name
        self.balance = balance
        self.active = active
        self.site_number = str(site_number)

        # If no aliases are supplied, construct a list from name and site number
        self.aliases = aliases if aliases is not None else []
        if len(self.aliases) == 1 or len(self.aliases) == 0:
            names = self.name.split(" ")
            self.aliases.pop()
            for alias in names:
                self.aliases.append(alias)
                self.aliases.append(alias.upper())
            self.aliases.append(self.site_number)
            self.aliases.append(str(site_number))

        # Normalises site number to two digits
        if len(self.site_number) == 1:
            self.site_number = f"0{self.site_number}"

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Account:
        """
        Constructs an instance from a row of a CSV file

        Args:
            row: The row of the CSV file

        Returns:
            The account instance containing the information from the row
        """

        # Nomarlises the active status of the account
        if (
            row["Active"] == "1"
            or row["Active"] == "None"
            or row["Active"] == "True"
            or row["Active"] == ""
        ):
            active = True
        else:
            active = False

        # Checks for and normalises the ID. If none is found it assigns None
        try:
            if row["ID"] == "None" or row["ID"] == "":
                id = None
            else:
                id = int(row["ID"])
        except KeyError:
            print("No ID Row Found")
            id = None

        # Construct the class
        return cls(
            site_number=row["Site"],
            name=row["Name"],
            aliases=row["Aliases"].split(","),
            account_id=id,
            active=active,
        )

    def add_balance(self, balance: Balance) -> None:
        """
        Add a balance to the account

        Args:
            balance: The balance to add
        """

        self.balance = balance

        # Assigns an account ID to the balance if one exists
        if self.account_id is not None:
            self.balance.account_id = self.account_id

    def change_site(self, new_site: str) -> None:
        """
        Change the site number of the account

        Args:
            new_site: The site number to change too
        """

        self.site_number = new_site

        # Adds new site number to existing aliases
        self.aliases.append(new_site)

        # Changes the site number of the assocciated balance
        if self.balance is not None:
            self.balance.site_number = new_site

    def change_name(self, new_name: str) -> None:
        """
        Change the name of the primary site holder

        Args:
            new_name: The name to change too
        """

        self.name = new_name

        # Adds new name to existing aliases
        new_name_split = new_name.split(" ")
        for name in new_name_split:
            self.aliases.append(name)
            self.aliases.append(name.upper())

    def switch_active(self) -> None:
        """Switch the active status of the account"""
        self.active = not self.active

    def add_alias(self, alias: str) -> bool:
        """
        Add a word to the existing aliases

        Args:
            alias: The word to add

        Returns:
            True if alias added. False if already already exists
        """

        if alias in self.aliases:
            return False
        else:
            self.aliases.append(alias)
            return True

    def to_dict(self) -> dict[str, str]:
        """
        Constructs a dictionary containing information required to reconstruct the account. Used for exporting to CSV

        Returns:
            A dictionary containing the account information
        """

        # Normalises the active status
        if self.active == True:
            active = "1"
        else:
            active = "0"

        return {
            "Name": self.name,
            "Site": str(self.site_number),
            "Aliases": ",".join(self.aliases),
            "Active": active,
        }

    def __str__(self) -> str:
        """
        A string representation of the account

        Returns:
            A string representation fo the account
        """

        return f"{self.site_number}: {self.name}"
