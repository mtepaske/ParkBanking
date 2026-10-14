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
        site: int | str,
        annual: float | str,
        remaining: float | str,
        outstanding: float | str,
        pay_period: Literal["m", "q", "a"] | str,
    ) -> None:
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
        expected = self.expected_paid(as_of_date)
        actual_paid = self.annual - self.remaining
        return actual_paid >= expected

    def to_dict(self) -> dict[str, str]:
        return {
            "Site": str(self.site),
            "Annual Fee": str(self.annual),
            "Remaining from this FY": str(self.remaining),
            "Outstanding from previous FYs": str(self.outstanding),
            "Pay Frequency": self.pay_frequency,
        }
