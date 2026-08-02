class Account:
    def __init__(self, site: str, name: str, aliases: list[str]):
        self.name = name
        self.site = site
        self.aliases = aliases

        if len(self.aliases) < 3:
            toadd = self.name.split(' ')
            toadd.append(site)
            self.aliases = toadd

    def getAlias(self) -> list[str]:
        return self.aliases

    def addAlias(self, alias: str) -> bool:
        if alias in self.aliases:
            return False
        else:
            self.aliases.append(alias)
            return True

    def __str__(self) -> str:
        return f'{self.site}: {self.name} --> {self.aliases}'
