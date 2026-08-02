class Account:
    def __init__(self, site: str, name: str, aliases: list[str]):
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
        return self.aliases

    def addAlias(self, alias: str) -> bool:
        if alias in self.aliases:
            return False
        else:
            self.aliases.append(alias)
            return True

    def getSite(self) -> str:
        return self.site

    def getName(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f'{self.site}: {self.name} --> {self.aliases}'
