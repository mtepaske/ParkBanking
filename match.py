from account import Account
from transactions import Transaction


class Matcher:
    """Handles matching of transactions to accounts

    Attributes:
        accounts: (list[Account]) A list of accounts to match to
        ignore: (list[str]) A list of words to ignore while matching
        unknown: (list[str]) A list of words that haven't been encountered before
    """

    def __init__(self, accounts: list[Account], ignore: list[str]):
        """Initialisaes class

        Args:
            accounts: (list[Account]) A list of accounts to match to
            ignore: (list[str]) A list of words to ignore while matching
        """
        self.accounts = accounts
        self.ignore = ignore
        self.unknown = []

    def cleanDesc(self, description: list[str]) -> list[str]:
        """Cleans the transaction details and removes any irrelavent words

        Args:
            description: (list[str]) A list of words from the transaction details

        Returns:
            (list[str]) A filtered list of words with irrelavent information removed
        """
        filtered = []
        for word in description:
            if word not in self.ignore:
                filtered.append(word)
        return filtered

    def printAccounts(self, accounts: list[Account] | None = None) -> None:
        """Print accounts to the terminal for user input

        Args:
            accounts: (list[Account]) A list of accounts to print
        """
        if accounts is None:
            accounts = self.accounts
        index = 1
        for account in accounts:
            print(f"[{index}] - {account.getName()}, Site {account.getSite()}")
            index += 1

    def accountPicker(self, accounts: list[Account] | None = None) -> Account:
        """Asks the user to input an account choice

        Args:
            accounts: (list[Account]) A list of accounts to choose from

        Returns:
            (Account) The users chosen account
        """
        if accounts is None:
            accounts = self.accounts
        self.printAccounts(accounts)
        while True:
            try:
                choice = int(input("Which Account? "))
                account = accounts[choice - 1]
                break
            except ValueError:
                print("Choice must be a number")
            except IndexError:
                print("Choice must be a valid index")
        print(f"You have picked {account}")
        return account

    def keywordMatch(self, transaction: Transaction) -> list[Account] | None:
        """Matches any relavent words in a transactions details to a account

        Args:
            transaction: (Transaction) A transaction to match

        Returns:
            (None) If no match can be made
            (list[Accounts]) If one or matches are found
        """
        possible = []
        details = self.cleanDesc(transaction.details)
        for word in details:
            found = False
            for account in self.accounts:
                if word in account.getAlias():
                    found = True
                    if account not in possible:
                        possible.append(account)
            if found is False and word not in self.unknown:
                self.unknown.append(word)
        if len(possible) == 0:
            return None
        else:
            return possible

    def noMatches(self, transaction: Transaction) -> None:
        """Prompts the user for a account choice when no matches can be found

        Args:
            transaction: (Transaction) The transaction to be matched
        """
        print(f"Details: {transaction.details}")
        print("Which Account does this payment belong to?")
        choice = self.accountPicker()
        transaction.addAccount(choice)

    def match(self, transaction: Transaction, possibilities: list[Account] | None):
        """Matches transactions if only one possibility was found, or prompts for user choice

        Args:
            transaction: (Transacrion) Trascation to match
            possibilities: (list[Account] | None) List of possible accounts if any were found
        """
        if possibilities is None:
            print("No Possible Matches Found")
            self.noMatches(transaction)
        elif len(possibilities) == 1:
            transaction.addAccount(possibilities[0])
            print(f"Match found: {possibilities[0]}")
        else:
            amount = len(possibilities)
            print(f"Details: {transaction.details}")
            print(f"{amount} Possible Choices Found")
            choice = self.accountPicker(possibilities)
            transaction.addAccount(choice)

    def aliasHandler(self, alias: str):
        """Handles choosing account to add alias to and adding the alias

        Args:
            alias: (str) The alias to add to the account
        """
        choice = self.accountPicker()
        choice.addAlias(alias)

    def ignoreHandler(self, word: str):
        """Handles adding words to ignored words

        Args:
            word: (str) Word to add to ignored word
        """
        self.ignore.append(word)

    def unknownWords(self):
        """Prompts the user for choice on what to do with unknown words"""
        for word in self.unknown:
            print(f"{word} is an unknown word, what would you like to do with it?")
            while True:
                choice = input(
                    "[i] - Add to ignored words\n"
                    "[a] - Add as an alias\n"
                    "[s] - skip\n"
                    "What is your choice? "
                )
                if choice in ["i", "a", "s"]:
                    break
                print("Choice invalid, please try again")
            if choice == "i":
                self.ignoreHandler(word)
                print(f"Ignored words: {self.ignore}")
            elif choice == "a":
                self.aliasHandler(word)
