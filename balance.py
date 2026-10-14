from __future__ import annotations

import datetime as dt
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal


class Balance:

    CENT = Decimal("0.01")

    @staticmethod
    def money(value: Decimal | float | str) -> Decimal:
        return Decimal(str(value)).quantize(Balance.CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def calc_months_left(date: dt.date) -> int:
        month = date.month
        if month >= 7:
            return 12 - month + 6
        else:
            return 6 - month

    @staticmethod
    def pay_period(
        num_of_payments: int = 12,
    ) -> Literal["Weekly", "Monthly", "Quarterly", "Half-Yearly", "Annual"]:
        if num_of_payments == 52:
            return "Weekly"
        elif num_of_payments == 4:
            return "Quarterly"
        elif num_of_payments == 2:
            return "Half-Yearly"
        elif num_of_payments == 1:
            return "Annual"
        else:
            return "Monthly"

    def __init__(
        self, site: int, annual: float, remaining: float, outstanding: float
    ) -> None:
        self.credit = Decimal("0.00")
        self.site = site
        self.annual = self.money(annual)
        self.remaining = self.money(remaining)
        self.outstanding = self.money(outstanding)

    @classmethod
    def from_csv(cls, filepath: str):
        pass

    @property
    def balance(self) -> Decimal:
        return self.outstanding + self.remaining

    @property
    def outstanding(self) -> Decimal:
        return self._outstanding

    @outstanding.setter
    def outstanding(self, amount: Decimal) -> None:
        amount = self.money(amount)
        if amount < 0:
            raise ValueError("Outstanding can not be negative")
        else:
            self._outstanding = amount

    @property
    def remaining(self) -> Decimal:
        return self._remaining

    @remaining.setter
    def remaining(self, amount: Decimal) -> None:
        amount = self.money(amount)
        if amount < 0:
            raise ValueError("Remaining can not be negative")
        else:
            self._remaining = amount

    def info(self, num_of_payments: int = 12) -> None:
        period = self.pay_period(num_of_payments)
        print(f"Balance info for Site {self.site}")
        print(f"  Total Annual Fees: {self.annual}")
        print(f"  Annual Fees Remaining: {self.remaining}")
        print(f"  Outstanding From Previous Years: {self.outstanding}")
        print(f"  {period} Payment: {self.calc_payments(self.annual, num_of_payments)}")

    def calc_payments(self, amount: Decimal, num_of_payments: int = 12) -> Decimal:
        if num_of_payments <= 0:
            raise ValueError("Number of payments must be greater then 0")
        return self.money(amount / num_of_payments)

    def add_payment(self, amount: Decimal) -> None:
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


if __name__ == "__main__":

    test = Balance(1, 7550, 7550, 0)
