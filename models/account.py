from __future__ import annotations

from models.balance import Balance


class Account:

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
        self.account_id = account_id
        self.name = name
        self.balance = balance
        self.active = active
        # Site number is extended to 2 digits
        self.site_number = str(site_number)
        if len(self.site_number) == 1:
            self.site_number = f"0{self.site_number}"
        self.aliases = aliases if aliases is not None else []
        # Aliases attribute is populated with name and site number if none given
        if len(self.aliases) == 0:
            names = self.name.split(" ")
            for alias in names:
                self.aliases.append(alias)
                self.aliases.append(alias.upper())
            self.aliases.append(self.site_number)
            self.aliases.append(str(site_number))

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Account:
        # Checks for all representations of active status
        if row["Active"] == "1" or row["Active"] == "None" or row["Active"] == "True":
            active = True
        else:
            active = False
        # Checks for a database ID, if none exists then it hasnt been assigned to the database before
        if row["ID"] == "None" or row["ID"] == "":
            id = None
        else:
            id = int(row["ID"])
        return cls(
            site_number=row["Site"],
            name=row["Name"],
            aliases=row["Aliases"].split(","),
            account_id=id,
            active=active,
        )

    def add_balance(self, balance: Balance) -> None:
        self.balance = balance
        if self.account_id is not None:
            self.balance.account_id = self.account_id

    def change_site(self, new_site: str) -> None:
        self.site_number = new_site
        self.aliases.append(new_site)
        if self.balance is not None:
            self.balance.site_number = new_site

    def change_name(self, new_name: str) -> None:
        self.name = new_name
        new_name_split = new_name.split(" ")
        for name in new_name_split:
            self.aliases.append(name)
            self.aliases.append(name.upper())

    def switch_active(self) -> None:
        self.active = not self.active

    def add_alias(self, alias: str) -> bool:
        if alias in self.aliases:
            return False
        else:
            self.aliases.append(alias)
            return True

    def to_dict(self) -> dict[str, str]:
        if self.active == True:
            active = "1"
        else:
            active = "0"
        return {
            "ID": str(self.account_id),
            "Name": self.name,
            "Site": str(self.site_number),
            "Aliases": ",".join(self.aliases),
            "Active": active,
        }

    def __str__(self) -> str:
        return f"{self.site_number}: {self.name}"
