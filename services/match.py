from cli.menu import get_input
from models.account import Account
from models.transactions import Transaction


class Matcher:
    """Handles matching of transactions to accounts

    Attributes:
        accounts: (list[Account]) A list of accounts to match to
        ignore: (list[str]) A list of words to ignore while matching
        unknown: (list[str]) A list of words that haven't been encountered before
    """

    @staticmethod
    def change_match(transaction: Transaction, accounts: list[Account]):
        choice = Matcher.account_picker(accounts)
        transaction.add_account(choice)

    def __init__(self, accounts: list[Account], ignore: list[str]) -> None:
        """Initialisaes class

        Args:
            accounts: (list[Account]) A list of accounts to match to
            ignore: (list[str]) A list of words to ignore while matching

        Returns:
            None
        """
        self.accounts = accounts
        self.ignore = ignore
        self.unknown = []

    def clean_desc(self, description: list[str]) -> list[str]:
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

    @staticmethod
    def print_accounts(accounts: list[Account]) -> None:
        """Print accounts to the terminal for user input

        Args:
            accounts: (list[Account]) A list of accounts to print

        Returns:
            None
        """
        index = 1
        for account in accounts:
            assert account.balance is not None
            print(f"[{index}] - {account.name}, Site {account.site}")
            index += 1
            balance = account.balance
            print(
                f"    Annual Fees: {balance.annual}, Remaining: {balance.remaining}, Outstanding: {balance.outstanding}, On Track: {balance.check_on_track()}"
            )

    @staticmethod
    def account_picker(accounts: list[Account]) -> Account:
        """Asks the user to input an account choice

        Args:
            accounts: (list[Account]) A list of accounts to choose from

        Returns:
            (Account) The users chosen account
        """
        Matcher.print_accounts(accounts)
        print("[n] - No Account")
        while True:
            try:
                choice = get_input("Which Account?")
                if choice == "n":
                    print("No match for this transaction")
                account = accounts[int(choice) - 1]
                break
            except (IndexError, ValueError):
                print("Choice must be a valid index")
        print(f"You have picked {account}")
        return account

    def keyword_match(self, transaction: Transaction) -> list[Account] | None:
        """Matches any relavent words in a transactions details to a account

        Args:
            transaction: (Transaction) A transaction to match

        Returns:
            (None) If no match can be made
            (list[Accounts]) If one or matches are found
        """
        possible = []
        details = self.clean_desc(transaction.details)
        for word in details:
            found = False
            for account in self.accounts:
                if word in account.aliases:
                    found = True
                    if account not in possible:
                        possible.append(account)
            if found is False and self.unknown is not None:
                for unknown in self.unknown:
                    if word == unknown:
                        break
                self.unknown.append(word)
        if len(possible) == 0:
            return None
        else:
            return possible

    def no_matches(self, transaction: Transaction) -> None:
        """Prompts the user for a account choice when no matches can be found

        Args:
            transaction: (Transaction) The transaction to be matched

        Returns:
            None
        """
        print(
            f"Date: {transaction.date}, Amount: {transaction.amount}, Details: {transaction.details}"
        )
        print("Which Account does this payment belong to?")
        choice = Matcher.account_picker(self.accounts)
        transaction.add_account(choice)

    def match(
        self, transaction: Transaction, possibilities: list[Account] | None
    ) -> None:
        """Matches transactions if only one possibility was found, or prompts for user choice

        Args:
            transaction: (Transacrion) Trascation to match
            possibilities: (list[Account] | None) List of possible accounts if any were found

        Returns:
            None
        """
        if possibilities is None:
            print("No Possible Matches Found")
            self.no_matches(transaction)
        elif len(possibilities) == 1:
            transaction.add_account(possibilities[0])
            print(f"Match found: {possibilities[0]}")
        else:
            amount = len(possibilities)
            print(f"Details: {transaction.details}")
            print(f"{amount} Possible Choices Found")
            choice = Matcher.account_picker(possibilities)
            transaction.add_account(choice)

    def alias_handler(self, alias: str) -> None:
        """Handles choosing account to add alias to and adding the alias

        Args:
            alias: (str) The alias to add to the account

        Returns:
            None
        """
        choice = Matcher.account_picker(self.accounts)
        choice.add_alias(alias)

    def ignore_handler(self, word: str) -> None:
        """Handles adding words to ignored words

        Args:
            word: (str) Word to add to ignored word

        Returns:
            None
        """
        self.ignore.append(word)

    def unknown_words(self) -> None:
        """Prompts the user for choice on what to do with unknown words

        Returns:
            None
        """
        if self.unknown is None:
            print("No unknown words to proccess")
            return
        for word in self.unknown:
            print(f"{word} is an unknown word, what would you like to do with it?")
            while True:
                choice = get_input(
                    "[i] - Add to ignored words\n"
                    "[a] - Add as an alias\n"
                    "[s] - skip\n"
                    "What is your choice?"
                )
                if choice in ["i", "a", "s"]:
                    break
                print("Choice invalid, please try again")
            if choice == "i":
                self.ignore_handler(word)
                print(f"Ignored words: {self.ignore}")
            elif choice == "a":
                self.alias_handler(word)
        self.unknown = None
