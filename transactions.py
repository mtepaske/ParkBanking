from account import Account


class Transaction:
    """Stores and manipulates transaction data

    Attributes:
        date: (str) Date of patyment
        amount: (int) Amount of payment
        account:
            (None) If there is no account matched for transaction yet
            (Account) The account that is matched to the payment
        details: (list[str]) The details of the payment
    """

    def __init__(self, date, amount: int, details: str):
        """Initialises transaction

        Args:
            date: (str) The date of the payment
            amount: (int) The amount of the payment
            details: (str) the deatils for the payment
        """
        self.date = date
        self.amount = amount
        self.account = None
        self.details = details.split(' ')

    def addAccount(self, account: Account):
        """Adds an account to the transaction

        Args:
            account: (Account) Account to add to the transaction
        """
        self.account = account
#       print(f'{account} Added to transaction')

    def getAccount(self):
        """Gets the account matched to the transaction

        Returns:
            (Account) Account matched to transaction
        """
        return self.account

    def toDict(self) -> None | dict:
        """Converts the transaction to a dictionary for exporting

        Returns:
            (dict) A dictionary representing the transaction
        """
        if self.account is None:
            return None
        return {
            'Date': self.date,
            'Site': self.account.getSite(),
            'Name': self.account.getName(),
            'Amount': self.amount
        }
