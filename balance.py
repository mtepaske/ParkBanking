from __future__ import annotations

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal
from zoneinfo import ZoneInfo


class Balance:

    CENT = Decimal("0.01")

    @staticmethod
    def get_today() -> date:
        return datetime.now(ZoneInfo("Australia/Melbourne")).date()

    @staticmethod
    def money(value: Decimal | float | str) -> Decimal:
        return Decimal(str(value)).quantize(Balance.CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def pay_period(
        num_of_payments: int = 12,
    ) -> Literal["Monthly", "Quarterly", "Annual"]:
        if num_of_payments == 4:
            return "Quarterly"
        elif num_of_payments == 1:
            return "Annual"
        else:
            return "Monthly"

    def __init__(
        self,
        site: int,
        annual: float,
        remaining: float,
        outstanding: float,
        pay_period: Literal["m", "q", "a"],
    ) -> None:
        self.credit = Decimal("0.00")
        self.site = site
        self.annual = self.money(annual)
        self.remaining = self.money(remaining)
        self.outstanding = self.money(outstanding)
        match pay_period:
            case "m":
                self.num_of_payments = 12
            case "q":
                self.num_of_payments = 4
            case "a":
                self.num_of_payments = 1

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

    @property
    def end_of_fy(self) -> date:
        today = self.get_today()
        if today.month >= 7:
            return date(today.year + 1, 6, 30)
        else:
            return date(today.year, 6, 30)

    @property
    def start_of_fy(self) -> date:
        today = self.get_today()
        if today.month >= 7:
            return date(today.year, 7, 1)
        else:
            return date(today.year - 1, 7, 1)

    def info(self) -> None:
        period = self.pay_period(self.num_of_payments)
        print(f"Balance info for Site {self.site}")
        print(f"  Total Annual Fees: {self.annual}")
        print(f"  Annual Fees Remaining: {self.remaining}")
        print(f"  Outstanding From Previous Years: {self.outstanding}")
        print(
            f"  {period} Payment: {self.calc_payments(self.annual, self.num_of_payments)}"
        )

    def calc_payments(self, amount: Decimal, num_of_payments: int = 0) -> Decimal:
        if num_of_payments < 0:
            raise ValueError("Number of payments must be greater then 0")
        elif num_of_payments == 0:
            num_of_payments = self.num_of_payments
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

    def expected_paid(self, as_of_date: date | None = None) -> Decimal:
        count = 0
        month_offset = 0
        pay_period = self.pay_period(self.num_of_payments)
        if as_of_date is None:
            as_of_date = self.get_today()
        if pay_period == "Annual":
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
                if pay_period == "Quarterly":
                    month_offset += 3
                else:
                    month_offset += 1
        return self.calc_payments(self.annual) * count

    def check_on_track(self, as_of_date: date | None = None) -> bool:
        expected = self.expected_paid(as_of_date)
        actual_paid = self.annual - self.remaining
        return actual_paid >= expected


if __name__ == "__main__":

    test = Balance(1, 7550, 7550, 0, pay_period="a")

    test.info()

    print(test.expected_paid())
    print(test.check_on_track())

    test.add_payment(Decimal(2000))

    test.info()
    print(test.check_on_track())
