class Account:
    """Stores and manipulates Account information

    Attributes:
        name: (str) Name of account holder
        site: (str) Site number
        aliases: (list[str]) Any keywords connected to the account,
            used for matching
    """

    def __init__(self, site: str, name: str, aliases: list[str]):
        """Initialises Account object

        Args:
            site: (str) Site Number
            name: (str) Name of Site Holder
            aliases: (list[str]) Any keywords connected to the account
        """
        self.name = name
        self.site = site
        self.aliases = aliases

        if len(self.aliases) == 1:
            toadd = self.name.split(' ')
            toadd.append(str(site))
            toadd.append(toadd[0].upper())
            toadd.append(toadd[1].upper())
            self.aliases = toadd

    def getAlias(self) -> list[str]:
        """Get list of aliases connected to Account

        Returns:
            list(str) Aliases connected to account
        """
        return self.aliases

    def addAlias(self, alias: str) -> bool:
        """Add a new alias to an account

        Args:
            alias: (str) Alias to add

        Returns:
            True: If alias added
            False: If alias already connected
        """
        if alias in self.aliases:
            print(f'{alias} is already an alias for Site {self.site}')
            return False
        else:
            self.aliases.append(alias)
            print(f'{alias} added as alias for Site {self.site}')
            return True

    def getSite(self) -> str:
        """Get site number for Account

        Returns:
            (str) Site Number
        """
        return self.site

    def getName(self) -> str:
        """Get Name of site holder for Account

        Returns:
            (str) Site holder name
        """
        return self.name

    def toDict(self) -> dict:
        """Turn account into a dictonary for exporting

        Returns:
            (dict) A dictionary representing the account
        """
        return {
            'Name': self.name,
            'Site': self.site,
            'Aliases': ','.join(self.aliases)
        }

    def __str__(self) -> str:
        """Prints Account as string

        Returns:
            (str) A string representing the Account
        """
        return f'{self.site}: {self.name} --> {self.aliases}'
