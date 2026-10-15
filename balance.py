from __future__ import annotations

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal
from zoneinfo import ZoneInfo


class Balance:
    """Tracks account balance information

    Attributes:
        CENT: (decimal) A class constant for determining value rounding significance
        credit: (str) Represents the amount of credit on an account
        site: (str) The site number assigned to the account
        annual: (str) The annual fees for the site
        remaining: (str) The remaining annual fees left to pay
        outstanding: (str) The outstanding fees from previous financial years
        pay_frequency: ('m', 'q', 'a') The indicated pay frequency
    """

    CENT = Decimal("0.01")

    @staticmethod
    def get_today() -> date:
        """Gets todays date

        Returns:
            (date) A date object representing todays date
        """
        return datetime.now(ZoneInfo("Australia/Melbourne")).date()

    @staticmethod
    def money(value: Decimal | float | str) -> Decimal:
        """Rounds a value to 2 significant values to represent money

        Args:
            value: (decimal | float | str) The value to round

        Returns:
            (decimal) The rounded value representing money
        """
        return Decimal(str(value)).quantize(Balance.CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def pay_period(
        num_of_payments: int = 12,
    ) -> Literal["Monthly", "Quarterly", "Annual"]:
        """Determines a human readable pay period

        Args:
            num_of_payments: (int) The number of pays in a year. Defaults to 12

        Returns:
            (str) A human readable pay period for use in printing
        """
        if num_of_payments == 4:
            return "Quarterly"
        elif num_of_payments == 1:
            return "Annual"
        else:
            return "Monthly"

    def __init__(
        self,
        site: str,
        annual: str,
        remaining: str,
        outstanding: str,
        pay_period: str,
    ) -> None:
        """Initialises the class

        Args:
            site: (str) The site number assigned to the account
            annual: (str) The annual fees for the site
            remaining: (str) The remaining annual fees left to pay
            outstanding: (str) The outstanding fees from previous financial years
            pay_frequency: ('m', 'q', 'a') The indicated pay frequency

        Raises:
            ValueError: If pay frequency is invalid. Must be 'm', 'q', or 'a'

        Returns:
            None
        """
        self.credit = Decimal("0.00")
        self.site = site
        self.annual = self.money(annual)
        self.remaining = self.money(remaining)
        self.outstanding = self.money(outstanding)
        if pay_period != "q" and pay_period != "m" and pay_period != "a":
            raise ValueError("Pay Frequency not defined, must be 'm', 'q', or 'a'")
        match pay_period:
            case "m":
                self.num_of_payments = 12
            case "q":
                self.num_of_payments = 4
            case "a":
                self.num_of_payments = 1
        self.pay_frequency = pay_period

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Balance:
        """Converts from a csv row to an instance of the Balance class

        Args:
            row: (disct[str, str]) A row of the csv file to covert

        Returns:
            None
        """
        site = row["Site"]
        annual = row["Annual Fee"]
        remaining = row["Remaining from this FY"]
        outstanding = row["Outstanding from previous FYs"]
        pay_period = row["Pay Frequency"]
        if remaining == "":
            remaining = annual
        if outstanding == "":
            outstanding = "0.00"
        return cls(
            site,
            annual,
            remaining,
            outstanding,
            pay_period,
        )

    @property
    def balance(self) -> Decimal:
        """The total balance of the account

        Returns:
            (decimal) The total account balance
        """
        return self.outstanding + self.remaining

    @property
    def outstanding(self) -> Decimal:
        """The outstanding amount from previous FYs

        Returns:
            (decimal) The outstanding amount from previous FYs
        """
        return self._outstanding

    @outstanding.setter
    def outstanding(self, amount: Decimal) -> None:
        """A setter method to validate the outstanding amount

        Args:
            amount: (decimal) The value to set to

        Raises:
            ValueError: If the amount is negative
        """
        amount = self.money(amount)
        if amount < 0:
            raise ValueError("Outstanding can not be negative")
        else:
            self._outstanding = amount

    @property
    def remaining(self) -> Decimal:
        """The remaining amount for this FYs fees

        Returns:
            (decimal) The remaining amount on this FYs fees
        """
        return self._remaining

    @remaining.setter
    def remaining(self, amount: Decimal) -> None:
        """A setter method to validate the remaining amount

        Args:
            amount: (decimal) The value to set to

        Raises:
            ValueError: If the amount is negative
        """
        amount = self.money(amount)
        if amount < 0:
            raise ValueError("Remaining can not be negative")
        else:
            self._remaining = amount

    @property
    def end_of_fy(self) -> date:
        """Finds the end of the current financial year

        Returns:
            (date) The date of the end of the current financial year
        """
        today = self.get_today()
        if today.month >= 7:
            return date(today.year + 1, 6, 30)
        else:
            return date(today.year, 6, 30)

    @property
    def start_of_fy(self) -> date:
        """Finds the start of the current financial year

        Returns:
            (date) The date of the end of the current financial year
        """
        today = self.get_today()
        if today.month >= 7:
            return date(today.year, 7, 1)
        else:
            return date(today.year - 1, 7, 1)

    def info(self) -> None:
        """Produces a human readable summary of the class

        Returns:
            None
        """
        period = self.pay_period(self.num_of_payments)
        print(f"Balance info for Site {self.site}")
        print(f"  Total Annual Fees: {self.annual}")
        print(f"  Annual Fees Remaining: {self.remaining}")
        print(f"  Outstanding From Previous Years: {self.outstanding}")
        print(
            f"  {period} Payment: {self.calc_payments(self.annual, self.num_of_payments)}"
        )

    def calc_payments(self, amount: Decimal, num_of_payments: int = 0) -> Decimal:
        """Calculates the incrimental payment to be fully paid off in a certain number of payments

        Args:
            amount: (decimal) The amount to be paid off
            num_of_payments: (int) The number of payments to be made. Defaults to number of payments indicated in instance

        Returns:
            (decimal) The incimental payment amount

        Raises:
            ValueError: If the number of payments is less then 0
        """
        if num_of_payments < 0:
            raise ValueError("Number of payments must be greater then 0")
        elif num_of_payments == 0:
            num_of_payments = self.num_of_payments
        return self.money(amount / num_of_payments)

    def add_payment(self, amount: Decimal) -> None:
        """Adds a payment

        Args:
            amount: (decimal) The amount of the payment

        Raises:
            ValueError: If the amount is less than or equal to 0
        """
        amount = self.money(amount)
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if amount < self.outstanding:
            self.outstanding -= amount
        elif amount < self.balance:
            amount -= self.outstanding
            self.outstanding = Decimal("0.00")
            self.remaining -= amount
        else:
            amount -= self.outstanding
            self.outstanding = Decimal("0.00")
            amount -= self.remaining
            self.remaining = Decimal("0.00")
            self.credit = amount

    def expected_paid(self, as_of_date: date | None = None) -> Decimal:
        """The amount that is expected to be paid off the current financial years fees, assuming that the correct incrimental amount has been paid

        Args:
            as_of_date: (date | None) The date to find the expecation of. Defaults to todays date

        Returns:
            (decimal) The amount of money that is expected to be paid
        """
        count = 0
        month_offset = 0
        if as_of_date is None:
            as_of_date = self.get_today()
        if self.pay_frequency == "a":
            if as_of_date >= date(self.end_of_fy.year, 1, 1):
                return self.annual
            else:
                return self.money("0")
        else:
            while True:
                year = self.start_of_fy.year + ((6 + month_offset) // 12)
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
        """Determines if the current financial years fees are on track to be 0.00 by the end of the current financial year

        Args:
            as_of_date: (date | None) The date to check against. Defaults to todays date

        Returns:
            (bool) True if on track. False if behind on payments
        """
        expected = self.expected_paid(as_of_date)
        actual_paid = self.annual - self.remaining
        return actual_paid >= expected

    def to_dict(self) -> dict[str, str]:
        """Converts this instance of the Balance class into a dictionary for exporting

        Returns:
            (dict[str, str]) A dictionary representing the balance
        """
        return {
            "Site": str(self.site),
            "Annual Fee": str(self.annual),
            "Remaining from this FY": str(self.remaining),
            "Outstanding from previous FYs": str(self.outstanding),
            "Pay Frequency": self.pay_frequency,
        }
