from account import Account
from transactions import Transaction


class Matcher:

    def __init__(self, accounts: list[Account], ignore: list[str]):
        self.accounts = accounts
        self.ignore = ignore
        self.unknown = []

    def cleanDesc(self, description: list[str]) -> list[str]:
        filtered = []
        for word in description:
            if word not in self.ignore:
                filtered.append(word)
        return filtered

    def printAccounts(self, accounts: list[Account] | None = None) -> None:
        if accounts is None:
            accounts = self.accounts
        index = 1
        for account in accounts:
            print(f'[{index}] - {account.getName()}, Site {account.getSite()}')
            index += 1

    def accountPicker(self, accounts: list[Account] | None = None) -> Account:
        if accounts is None:
            accounts = self.accounts
        self.printAccounts(accounts)
        while True:
            try:
                choice = int(input('Which Account? '))
                account = accounts[choice - 1]
                break
            except ValueError:
                print('Choice must be a number')
            except IndexError:
                print('Choice must be a valid index')
        print(f'You have picked {account}')
        return account

    def keywordMatch(self, transaction: Transaction) -> list[Account] | None:
        possible = []
        details = self.cleanDesc(transaction.details)
#       print(f'Transaction Details: {details}')
        for word in details:
            found = False
            for account in self.accounts:
                if word in account.getAlias():
                    found = True
                    if account not in possible:
                        possible.append(account)
            if found is False:
                if word not in self.unknown:
                    self.unknown.append(word)
        if len(possible) == 0:
            return None
        else:
            return possible

    def noMatches(self, transaction: Transaction) -> None:
        print('Which Account does this payment belong to?')
        choice = self.accountPicker()
        transaction.addAccount(choice)

    def match(self, transaction: Transaction, possibilities: list[Account] | None):
        if possibilities is None:
            print('No Possible Matches Found')
            self.noMatches(transaction)
        elif len(possibilities) == 1:
            transaction.addAccount(possibilities[0])
            print(f'Match found: {possibilities[0]}')
        else:
            amount = len(possibilities)
            print(f'{amount} Possible Choices Found')
            choice = self.accountPicker(possibilities)
            transaction.addAccount(choice)

    def aliasHandler(self, alias: str):
        choice = self.accountPicker()
        choice.addAlias(alias)

    def ignoreHandler(self, word: str):
        self.ignore.append(word)

    def unknownWords(self):
        for word in self.unknown:
            print(f'{word} is an unknown word, what would you like to do with it?')
            while True:
                choice = input(
                    '[i] - Add to ignored words\n'
                    '[a] - Add as an alias\n'
                    '[s] - skip\n'
                    'What is your choice? '
                )
                if choice in ['i', 'a', 's']:
                    break
                print('Choice invalid, please try again')

            if choice == 'i':
                self.ignoreHandler(word)
                print(f'Ignored words: {self.ignore}')
            elif choice == 'a':
                self.aliasHandler(word)
