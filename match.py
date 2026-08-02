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

    def keywordMatch(self, transaction: Transaction) -> list[Account] | None:
        possible = []
        details = self.cleanDesc(transaction.details)
        print(f'Transaction Details: {details}')

        for word in details:
            found = False
            for account in self.accounts:
                if word in account.getAlias():
                    if account not in possible:
                        found = True
                        possible.append(account)

            if found is False:
                if word not in self.unknown:
                    self.unknown.append(word)

#       print('Possible Accounts:')
#       for account in possible:
#           print(account)

        if len(possible) == 0:
            return None
        else:
            return possible

    def match(self, transaction: Transaction, possibilities:
              list[Account] | None):
        if possibilities is None:
            print('No Possible Matches Found')
        elif len(possibilities) == 1:
            transaction.addAccount(possibilities[0])
            print(f'Match found: {possibilities[0]}')
        else:
            amount = len(possibilities)
            print(f'{amount} Possible Choices Found')
            index = 1
            for possibility in possibilities:
                print(f'''[{index}] - {possibility.getName()},
                      Site {possibility.getSite()}''')
                index += 1

            while True:
                choice = input(
                    'Account Choice?'
                )
                if int(choice) > amount | int(choice) < 1:
                    print('Choice not valid')
                break

            choiceint = int(choice)
            print(f'You have chosen account {possibilities[choiceint - 1]}')
            transaction.addAccount(possibilities[choiceint - 1])
            print('Account added to transaction')

    def unknownWords(self):
        for word in self.unknown:
            print(f'''{word} is an unknown word, what would you like to do with it?''')
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
                self.ignore.append(word)
                print('Word added to list of ignored words')
                print(f'Ignored words: {self.ignore}')
            elif choice == 'a':
                index = 1
                for account in self.accounts:
                    print(f'''[{index}] - {account.getName()}, Site {account.getSite()}''')
                    index += 1
                while True:
                    choice = input('Which Account?')
                    if int(choice) > len(self.accounts):
                        print('Invalid Account Number')
                    else:
                        self.accounts[int(index) - 1].addAlias(word)
