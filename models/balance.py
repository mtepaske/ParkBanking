from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from services.date import end_of_fy, get_today, start_of_fy

# The significant digits to round to
CENT = Decimal("0.01")


def money(value: Decimal | float | str) -> Decimal:
    """
    Normalises values to 2 decimal places. To represent monetary values

    Args:
        value: The value to normalise

    Returns:
        The normalised value
    """

    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


class Balance:
    """
    Tracks balance information

    Attributes:
        account_id: (int) The ID for the associated account. Gets assigned on accounts first insertion
        site_number: (str) The site number for the account
        annual: (Decimal) The amount of annual fees for current financial period
        remaining: (Decimal) The amount of remaining fees for the current financial period
        outstanding: (Decimal) The amount of outstanding fees from previous financial periods
        pay_frequency: ('m', 'q', 'a') The indicated payment frequency
        credit: (Decimal) The amount of credit. Defaults to $0
        balance_id: (int) The ID used for database queries. Gets assigned on first insertion
    """

    def __init__(
        self,
        account_id: int | None,
        site_number: str | int,
        annual: str,
        remaining: str,
        outstanding: str,
        pay_frequency: str,
        credit: str = "0.00",
        balance_id: int | None = None,
    ) -> None:
        """
        Initialises the class

        Args:
            account_id: The ID for the associated account. Gets assigned on accounts first insertion to database
            site_number: The site number of the associated account
            annual: The annual fees for the current financial period
            remaining: The remaining fees for the current financial period
            outstanding: The outstanding fees from prvious financial periods
            pay_frequency: The indicated paymnet frequency
            credit: The amount of credit
            id: The ID used for database queries. Gets assigned on first insertion
        """

        self.balance_id = balance_id
        self.account_id = account_id
        self.site_number = str(site_number)

        # Nomarlises the site number to two digits
        if len(self.site_number) == 1:
            self.site_number = f"0{self.site_number}"

        # Assigns fees as monetary amounts
        self.annual = money(annual)
        self.remaining = money(remaining)
        self.outstanding = money(outstanding)
        self.credit = money(credit)

        # Checks for valid pay frequency. If its invalid it reassigns as monthly
        try:
            if pay_frequency not in ["a", "q", "m"]:
                raise ValueError("Invalid Pay Frequency, reassigning to m")
        except ValueError:
            pay_frequency = "m"
        self.pay_frequency = pay_frequency

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Balance:
        """
        Constructs an instance from a row of a CSV file

        Args:
            row: The row of the CSV file

        Returns:
            The balance class containing the information from the row
        """

        site_number = row["Site Number"]
        annual = row["Annual Fee"]
        remaining = row["Remaining from this FY"]
        outstanding = row["Outstanding from previous FYs"]
        pay_frequency = row["Pay Frequency"]
        account_id = row["Account ID"]
        balance_id = row["Balance ID"]

        # Checks for and normalises the account ID. If none is found it assigns None
        if account_id == "None" or account_id == "":
            account_id = None
        else:
            account_id = int(account_id)

        # Checks for and normalises the ID. If none is found it assigns None
        if balance_id == "None" or balance_id == "":
            balance_id = None
        else:
            balance_id = int(balance_id)

        # Checks for remaining amount. If the row is empty assigns the annual amount. If its negative assigns as credit instead
        if remaining == "":
            remaining = annual
        if Decimal(remaining) < 0:
            credit = str(Decimal(remaining) * -1)
            remaining = "0.00"
        else:
            credit = "0.00"

        # Checks for outstanding amount. If the row is empty assigns 0
        if outstanding == "":
            outstanding = "0.00"

        # Construct the class
        return cls(
            account_id=account_id,
            site_number=site_number,
            annual=annual,
            remaining=remaining,
            outstanding=outstanding,
            pay_frequency=pay_frequency,
            credit=credit,
            balance_id=balance_id,
        )

    @property
    def balance(self) -> Decimal:
        """The total fees owed"""

        return (self.outstanding + self.remaining) - self.credit

    @property
    def outstanding(self) -> Decimal:
        """The fees outsanding from previous financial periods"""

        return self._outstanding

    @outstanding.setter
    def outstanding(self, amount: Decimal) -> None:
        """
        Sets the outstanding fees

        Args:
            amount: The amount to set too

        Raises:
            ValueError: If the amount is negative
        """

        amount = money(amount)
        if amount < 0:
            raise ValueError("Outstanding can not be negative")
        else:
            self._outstanding = amount

    @property
    def remaining(self) -> Decimal:
        """The remianing fees from this financial period"""

        return self._remaining

    @remaining.setter
    def remaining(self, amount: Decimal) -> None:
        """Sets the remaining fees

        Args:
            amount: The amount to set too

        Raises:
            ValueError: If the amount is negative
        """

        amount = money(amount)
        if amount < 0:
            raise ValueError("Remaining can not be negative")
        else:
            self._remaining = amount

    def change_payfrequency(self, new_frequency: Literal["a", "q", "m"]):
        """
        Changes the pay frequency

        Args:
            new_frequency: Frequency to change to
        """

        self.pay_frequency = new_frequency

    def calc_payments(self, balance: Decimal, num_of_payments: int = 0) -> Decimal:
        """
        Calculates the amount a regular paymnet would have to be to have a 0 balance by the end of the fincial period

        Args:
            balance: The balance to pay
            num_of_payments: The number of regular payments. Defaults to indicated number of paymnets given indicated pay frequency

        Returns:
            The amount a regular paymnet would have to be

        Raises:
            ValueError: If the number of payments is less than 0
        """

        if num_of_payments < 0:
            raise ValueError("Number of payments must be greater then 0")

        # Finds the number of paymnets given the indicated pay frequency
        elif num_of_payments == 0:
            match self.pay_frequency:
                case "a":
                    num_of_payments = 1
                case "q":
                    num_of_payments = 4
                case "m":
                    num_of_payments = 12

        return money(balance / num_of_payments)

    def add_payment(
        self,
        amount: Decimal,
        initial: tuple[Decimal, Decimal, Decimal] | None = None,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Returns what the new balance would be if a payment is added

        Args:
            amount: The amount to remove
            initial: The balance amounts to work off. Defaults to current amounts

        Returns:
            A tuple containing the new balance amounts

        Raises:
            ValueError: If the amount is negative
        """

        # Assign initial amounts
        if initial is None:
            remaining = self.remaining
            outstanding = self.outstanding
            credit = self.credit
            balance = self.balance

        else:
            remaining, outstanding, credit = initial
            balance = remaining + outstanding - credit

        # Normalise the amount to represent money
        amount = money(amount)

        # Validation
        if amount < 0:
            raise ValueError("Amount must be greater than 0")

        # First removed from outstanding fees
        if amount < outstanding:
            outstanding -= amount

        # Then removes from remaining fees
        elif amount < balance:
            amount -= outstanding
            outstanding = Decimal("0.00")
            remaining -= amount

        # Adds left over amount to credit
        else:
            amount -= outstanding
            outstanding = Decimal("0.00")
            amount -= remaining
            remaining = Decimal("0.00")
            credit += amount

        return (remaining, outstanding, credit)

    def add_charge(
        self,
        amount: Decimal,
        balance_amounts: tuple[Decimal, Decimal, Decimal] | None = None,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Returns what the new balance would be if a charge is added

        Args:
            amount: The amount to add
            initial: The balance amounts to work off. Defaults to current amounts

        Returns:
            A tuple containing the new balance amounts

        Raises:
            ValueError: If the amount is positive
        """

        # Assign initial amounts
        annual = self.annual
        if balance_amounts is None:
            remaining = self.remaining
            outstanding = self.outstanding
            credit = self.credit
        else:
            remaining, outstanding, credit = balance_amounts

        # Validation
        if amount > 0:
            raise ValueError("Amount Must Be Less Than 0")
        amount = money(amount)

        # Convert to positive value
        amount = abs(amount)
        remaining += amount

        # If there is any credit, reduce remianing amount
        if credit > Decimal(0):

            # If the remaining is more then credit
            if credit < remaining:
                remaining -= credit
                credit = Decimal(0)

            # If remaining is less then the credit
            else:
                credit -= remaining
                remaining = Decimal(0)

        # If remaining is more then annual fees, add it to outstanding
        if remaining > annual:
            outstanding += remaining - annual
            remaining -= outstanding

        return (remaining, outstanding, credit)

    def apply_new_amounts(self, amounts: tuple[Decimal, Decimal, Decimal]) -> None:
        """
        Applies new balance amounts calculated from add_charge or add_payment

        Args:
            amounts: A tuple containing new balance amounts
        """

        self.remaining = amounts[0]
        self.outstanding = amounts[1]
        self.credit = amounts[2]

    def expected_paid(self, as_of_date: date | None = None) -> Decimal:
        """
        Calculates the expected amount to be paid off the remaining fees. Given the indicated pay frequency

        Args:
            as_of_date: The date to calculate the amount for. Defaults to todays date

        Returns:
            The amount that is expected to be paid
        """

        count = 0
        month_offset = 0

        # Assigns todays date if none supplied
        if as_of_date is None:
            as_of_date = get_today()

        # If the pay frequency is annual. Check if before due date
        if self.pay_frequency == "a":
            if as_of_date >= date(end_of_fy().year, 1, 1):
                return self.annual
            else:
                return money("0")

        # Calculates the amount expected to have been paid
        else:
            while True:
                year = start_of_fy().year + ((6 + month_offset) // 12)
                month = (6 + month_offset) % 12 + 1
                due_date = date(year, month, 15)
                if due_date >= as_of_date:
                    break
                count += 1
                if self.pay_frequency == "q":
                    month_offset += 3
                else:
                    month_offset += 1

        return self.calc_payments(self.annual) * count

    def check_on_track(self, as_of_date: date | None = None) -> bool:
        """
        Checks if the account is on track to have a balance of 0 at the end of the fincial period by using the expected paid vs the actual paid

        Args:
            as_of_date: The date to check against

        Returns:
            True if on track. False if theres an outstanding amount or if not on track
        """

        # Checks for outstanding amount
        if self.outstanding != money(0):
            return False
        expected = self.expected_paid(as_of_date)
        actual_paid = self.annual - self.remaining
        return actual_paid >= expected

    def recalculate_from_history(
        self, history: list
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Recalculate the current balance amounts from the account history

        Args:
            history: A list of charges and payments

        Returns:
            A tuple containing the new balance amounts
        """

        # Set inital amounts to 0
        remaining = money("0")
        outstanding = money("0")
        credit = money("0")

        for transaction in history:

            # If the amount is negative
            if transaction.amount > 0:
                remaining, outstanding, credit = self.add_payment(
                    transaction.amount, (remaining, outstanding, credit)
                )
            # If the amount is positive
            else:
                remaining, outstanding, credit = self.add_charge(
                    transaction.amount, (remaining, outstanding, credit)
                )

        return (remaining, outstanding, credit)

    def to_dict(self) -> dict[str, str]:
        """
        Constructs a dictionary containing information required to reconstruct the balance. Used for exporting to CSV

        Returns:
            A dictionary containing the account information
        """

        id = str(self.balance_id)
        account_id = str(self.account_id)
        site_number = str(self.site_number)
        annual = str(self.annual)
        remaining = self.remaining
        outstanding = str(self.outstanding)
        pay_frequency = self.pay_frequency

        # Converts credit into a negative remaining amount
        if self.credit != money(0):
            remaining -= self.credit
        remaining = str(remaining)

        return {
            "Site": site_number,
            "Annual Fee": annual,
            "Remaining from this FY": remaining,
            "Outstanding from previous FYs": outstanding,
            "Pay Frequency": pay_frequency,
            "Account ID": account_id,
            "Balance ID": id,
        }

    def __str__(self) -> str:
        """
        A string representation of the balance

        Returns:
            A string representation fo the balance
        """
        return f"Balance for {self.site_number} with Account ID {self.account_id} -> Annual = {self.annual}, Remaining = {self.remaining}, Outstanding = {self.outstanding}, Credit = {self.credit}, Pay Frequency = {self.pay_frequency}"
